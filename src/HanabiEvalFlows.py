from copy import deepcopy
from HanabiDeductionFlows import *
from HanabiConventionFlows import *

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
	temptab = BitTable(game,pl=player)
	temptab.update_location_list(game)
	temptab.update_critical_list(game)
	for card in game.play.deck:
		temptab.add_bit(Hanabit("confirmed","color",card.color,"final",temptab),card)
		temptab.add_bit(Hanabit("confirmed","number",card.number,"final",temptab),card)
	for card in game.discard.deck:
		temptab.add_bit(Hanabit("confirmed","color",card.color,"final",temptab),card)
		temptab.add_bit(Hanabit("confirmed","number",card.number,"final",temptab),card)
	for pl in game.players:
		for card in game.decks[pl.name].deck:
			if (pl.name != player.name and pl.name != other.name):
				temptab.add_bit(Hanabit("confirmed","color",card.color,"final",temptab),card)
				temptab.add_bit(Hanabit("confirmed","number",card.number,"final",temptab),card)
	#Consult the log to find all clues given regarding 
	#cards *currently* not visible to each of the two players.
	#Add only the content of those clues to the temp table
	#This will have to change when rainbow is added back in.
	for ev in game.past_log:
		if (ev.type == "Clue" and (ev.tgt == player.name or ev.tgt == other.name)):
			DeductionBot(game.variant).receive_clue(ev,temptab)
	game.con.order_play_q(temptab)
	game.con.order_discard_q(temptab)
	return temptab

def eval_flow(player,game):
	chs = create_all_choices(player,game)
	clocks_are_low = (game.MAX_CLOCKS/2) - game.clocks
	# go through the hand. score playables, score others as discardable
	for enum, c in enumerate(game.decks[player.name].deck):
		if player.trike.tab.list[c].query_bit_pile(qtype=["confirmed","conventional"] 
											  ,qquality=["playability"]
											  ,qvalue=["playable"]
											  ,qspin=["pos","final"]):
			for i in chs:
				if i.action == "Play" and i.pos == (len(game.decks[player.name].deck) - enum):
					i.bump(10)
		elif player.trike.tab.list[c].query_bit_pile(qtype=["default","conventional"] 
											    ,qquality=["discardability"]
											    ,qvalue=["discardable"]
												,qspin=["default","pos","final"]):
			for i in chs:
				if i.action == "Discard" and i.pos == (len(game.decks[player.name].deck) - enum):
					qpos = i.tgt.trike.tab.discard_q.index(c)
					i.bump(1 + len(i.tgt.trike.tab.discard_q) - qpos) 
	# evaluate clues based on type of clue theyll think it is
	for i in chs:
		if i.action == "Clue":
			pred = game.con.predict_clue(HanabiEvent(player,i.tgt,"Clue",None,i.color,i.number)
			                             ,ikyk(game,player,i.tgt)
										 ,game)
			if pred == "playing":
				i.bump(9)
			elif pred == "bombing":
				i.bump(-10)
			elif pred == "protective":
				i.bump(8)
			elif pred == "dud":
				i.bump(-10)
			#these ones are just not implemented yet...
			elif pred == "multi-play":
				i.bump(-10)
			elif pred == "stalling":
				i.bump(-10)
			
	return chs.sort()
	
def create_comp_tab(player):
	return deepcopy(player.trike.tab)
	
def pos_to_card(player,pos):
	for card in player.trike.tab.location[player.name]:
		if player.trike.tab.list[card].query_bit_pile(qquality="position",qvalue=pos):
			return card
	#convert a hand position into a card that can be 
	#used to create an Event

	
	
def event_from_choice(choice,player,game):
	if choice.action != "Clue":
		card_id = game.decks[player.name].deck[len(game.decks[player.name].deck)-choice.pos].id 	
	else:
		card_id = None
		
	return HanabiEvent(player,choice.tgt,choice.action,card_id,choice.color,choice.number)
		