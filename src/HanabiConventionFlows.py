

### We need to work on solidifying our list of qualities and values

class HanabiConventions(object):
	def __init__(self,game):
		self.bot = game.bot

	def oldest(self,card_list,table):
		positions = []
		position_dict = {}
		for card in card_list:
			for bit in table.list[card].quality_pile["position"]:
				positions.append(bit.value)
				position_dict[bit.value] = card
		positions.sort()
		return position_dict[positions[-1]]
						
	def newest(self,card_list,table):
		positions = []
		position_dict = {}
		for card in card_list:
			for bit in table.list[card].quality_pile["position"]:
				positions.append(bit.value)
				position_dict[bit.value] = card
		positions.sort()
		return position_dict[positions[0]]

		
class PlayConventions(HanabiConventions):
	def __init__(self,game,active_player):
		HanabiConventions.__init__(game)
	
	def possible(self,table):
		event_list = []
		for card in table.location[table.name]:
			if table.bool_query(qcard=card,qquality="playability",qspin="pos") or table.bool_query(qcard=card,qquality="playability",qspin="final"):
				event_list.append( HanabiEvent(table.name,None,"Play",card.id,card.color,card.number))
		return event_list

class DiscardConventions(HanabiConventions):
	def __init__(self,game):
		HanabiConventions.__init__(game)

	def possible(self,table):
		event_list = []
		for card in table.location[table.name]:
			if table.bool_query(qcard=card,qquality="discardability",qvalue = "trash", qspin="final") or (table.bool_query(qcard=card,qquality="discardability",qvalue="discardable",qspin="pos") and not table.bool_query(qcard=card,qquality="playability",qvalue="playable",qspin ="pos")):
				event_list.append( HanabiEvent(table.name,None,"Discard",card.id,card.color,card.number))
		return event_list
		
class ClueConventions(HanabiConventions):
	def __init__(self,game):
		HanabiConventions.__init__(game)
				
	def possible(self,table):
		event_list = []
		for p in self.players:
			if p.name != table.name:
				for color in self.bot.decktemplate.colors:
					event_list.append(HanabiEvent(table.name,p.name,"Clue",None,color,None))
				for number in self.bot.decktemplate.colors:
					event_list.append(HanabiEvent(table.name,p.name,"Clue",None,None,number))
		return event_list
				
	def interpret_clue(self,table,game):			
		#prepare bools
		protective = False
		playing = False
		stalling = False
		
		
		if(protective):
			card_list = [x for x in table.location[table.name]]
			
		if(playing):
			pass
		if(stalling):
		#not sure what this is gonna be
			pass
				
				
				
				
				
				
				
				