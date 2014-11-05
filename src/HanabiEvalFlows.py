from copy import deepcopy
class Choice(object):
	def __init__(self,action=None,tgt=None,color=None,number=None,pos=None):
		self.action = action
		self.tgt = tgt
		self.color = color
		self.number = number
		self.pos = pos
		self.score = 0
		
	def __lt__(self,other):
		return self.score < other.score
		
	def bump(self,by):
		self.score = self.score + by

def create_all_choices(player,game):
	allc = []
	#Create plays and discards
	p = [Choice(action = "Play",pos = x+1) for x in range(game.variant.handsize)]
	d = [Choice(action = "Discard",pos = x+1) for x in range(game.variant.handsize)]
	#Create clues
	c = []
	for pl in game.players:
		if pl.name != player.name:
			c = c + [Choice(action = "Clue",tgt = pl.name,color = cl) for cl in game.colors]
			c = c + [Choice(action = "Clue",tgt = pl.name,number = nm) for nm in game.numbers]
	allc = p + d + c
	return allc
	
def ikyk(game,player,other):
	temptab = BitTable(game)
	for card in game.play.deck:
		temptab.add_bit(Hanabit("confirmed","color",card.color,"final",temptab),card)
		temptab.add_bit(Hanabit("confirmed","number",card.number,"final",temptab),card)
		temptab.add_bit(Hanabit("confirmed","location","Play","final",temptab),card)
	for card in game.discard.deck:
		temptab.add_bit(Hanabit("confirmed","color",card.color,"final",temptab),card)
		temptab.add_bit(Hanabit("confirmed","number",card.number,"final",temptab),card)
		temptab.add_bit(Hanabit("confirmed","location","Discard","final",temptab),card)
	for pl in game.players:
		if (pl.name != player.name and pl.name != other.name):
			for card in game.decks[pl.name].deck:
				temptab.add_bit(Hanabit("confirmed","color",card.color,"final",temptab),card)
				temptab.add_bit(Hanabit("confirmed","number",card.number,"final",temptab),card)
				temptab.add_bit(Hanabit("confirmed","location",pl.name,"final",temptab),card)
	#Consult the log to find all clues given regarding 
	#cards *currently* not visible to each of the two players.
	#Add only the content of those clues to the temp table
	#This will have to change when rainbow is added back in.
	for ev in game.past_log:
		if (ev.type == "Clue" and ev.touch and (ev.tgt == player.name or ev.tgt == other.name)):
			for card in ev.touch:
				if (ev.tgt == player.name and card in game.decks[player.name].deck):
					if ev.color:
						temptab.add_bit(Hanabit("confirmed","color",ev.color,"final",temptab),card)
					elif ev.number:
						temptab.add_bit(Hanabit("confirmed","number",ev.number,"final",temptab),card)		
				if (ev.tgt == other.name and card in game.decks[other.name].deck):
					if ev.color:
						temptab.add_bit(Hanabit("confirmed","color",ev.color,"final",temptab),card)
					elif ev.number:
						temptab.add_bit(Hanabit("confirmed","number",ev.number,"final",temptab),card)
	return temptab
		
def create_comp_tab(player):
	return deepcopy(player.trike.tab)
	
def pos_to_card(player,pos):
	for card in player.trike.tab.location[player.name]:
		if player.trike.tab.list[card].query_bit_pile(qquality="position",qvalue=pos):
			return card
	#convert a hand position into a card that can be 
	#used to create an Event