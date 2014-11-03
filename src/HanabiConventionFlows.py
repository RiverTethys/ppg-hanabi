

### We need to work on solidifying our list of qualities and values

class HanabiConventions(object):
	def __init__(self,game):
		self.bot = game.bot

		

class PlayConventions(HanabiConventions):
	def __init__(self,game,active_player):
		HanabiConventions.__init__(game)
	
	def possible(self,table):
		event_list = []
		for card in table.location[table.name]:
			if table.list[card].query_bit_pile(qcard=card,qquality=["playability"],qspin=["pos"]) or table.list[card].query_bit_pile(qcard=card,qquality=["playability"],qspin=["final"]):
				event_list.append( HanabiEvent(table.name,None,"Play",card.id,card.color,card.number))
		return event_list

class DiscardConventions(HanabiConventions):
	def __init__(self,game):
		HanabiConventions.__init__(game)

	def possible(self,table):
		event_list = []
		for card in table.location[table.name]:
			if table.list[card].query_bit_pile(qcard=card,qquality=["discardability"],qvalue = ["trash"], qspin=["final"]) or (table.list[card].query_bit_pile(qcard=card,qquality=["discardability"],qvalue=["discardable"],qspin=["pos"]) and not table.list[card].query_bit_pile(qcard=card,qquality=["playability"],qvalue=["playable"],qspin =["pos"])):
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
				
				
				
				
				
				
				
				
				
				
				
				