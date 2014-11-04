

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

		
#class PlayConventions(HanabiConventions):
	#def __init__(self,game,active_player):
		#HanabiConventions.__init__(game)
	
	# def possible(self,table):
		# event_list = []
		# for card in table.location[table.name]:
			# if table.list[card].query_bit_pile(qcard=card,qquality=["playability"],qspin=["pos"]) or table.list[card].query_bit_pile(qcard=card,qquality=["playability"],qspin=["final"]):
				# event_list.append( HanabiEvent(table.name,None,"Play",card.id,card.color,card.number))
		# return event_list

#class DiscardConventions(HanabiConventions):
	#def __init__(self,game):
		#HanabiConventions.__init__(game)

	# def possible(self,table):
		# event_list = []
		# for card in table.location[table.name]:
			# if table.list[card].query_bit_pile(qcard=card,qquality=["discardability"],qvalue = ["trash"], qspin=["final"]) or (table.list[card].query_bit_pile(qcard=card,qquality=["discardability"],qvalue=["discardable"],qspin=["pos"]) and not table.list[card].query_bit_pile(qcard=card,qquality=["playability"],qvalue=["playable"],qspin =["pos"])):
				# event_list.append( HanabiEvent(table.name,None,"Discard",card.id,card.color,card.number))
		# return event_list
		
#class ClueConventions(HanabiConventions):
#	def __init__(self,game):
#		HanabiConventions.__init__(game)
				
	# def possible(self,table):
		# event_list = []
		# for p in self.players:
			# if p.name != table.name:
				# for color in self.bot.decktemplate.colors:
					# event_list.append(HanabiEvent(table.name,p.name,"Clue",None,color,None))
				# for number in self.bot.decktemplate.colors:
					# event_list.append(HanabiEvent(table.name,p.name,"Clue",None,None,number))
		# return event_list
	
	
	
	def predict_clue(self,ev,table):
		#possible ways the clue could go.
		protective = False
		playing = False
		stalling = False
		multi_play = False
		bombing = False
		
	
	
	def interpret_clue(self,ev,table,game):			
		#prepare bools
		protective = False
		playing = False
		stalling = False
		multi-play = False #ohgodohgodohgod
		
		indicated_card = self.newest(table.clued_cards(ev))
		
		### could make room for stalling and multi_play
		
		# if clued about a "totally" unplayable card, then it's protective
		if table.list[indicated_card].query_bit_pile(qtype=["confirmed"],qvalue=["playable"],qspin=["neg"]):
			protective = True
		else:
			playing = True
		
		#resolve bools
		if(protective):
			protected_card = table.discard_q[0]
			Ibit = Hanabit("conventional","discardability","discardable","neg")
			table.add_bit(Ibit,protected_card)		
	
		if(playing):
			playable_card = self.newest(table.clued_cards(ev),table)
			Ibit = Hanabit("conventional","playability","playable","pos")
			table.add_bit(Ibit,indicated_card)
			if indicated_card in table.play_q:
				table.play_q.remove(indicated_card)
			table.play_q.appendleft(indicated_card)
			
		if (multi-play):
		#ohgodohgodohgod	
			pass
		
		if(stalling):
		#not sure what this is gonna be, if anything
			pass
		
		
				
				
				
				
				
				
				