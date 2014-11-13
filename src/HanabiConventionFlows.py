

### We need to work on solidifying our list of qualities and values


from HanabiDeductionFlows import *
from HanabiClasses import *

class HanabiConventions(object):
	def __init__(self,game):
		self.bot = game.bot

	def oldest(self,card_list,table,game): #returns card in oldest position from a list of cards, a subset of someone's hand
		table.update_positions(game)
		positions = []
		position_dict = {}
		for card in card_list:
			for bit in table.list[card].quality_pile["position"]:
				positions.append(bit.value)
				position_dict[bit.value] = card
		positions.sort()
		return position_dict[positions[-1]]
						
	def newest(self,card_list,table,game): #returns the newest card from a subset of a hand
		table.update_positions(game)
		positions = []
		position_dict = {}
		for card in card_list:
			for bit in table.list[card].quality_pile["position"]:
				positions.append(bit.value)
				position_dict[bit.value] = card
		if (positions):
			positions.sort()
			return position_dict[positions[0]]

	

	def order_play_q(self,table): #put certainly playable cards before conventionally playable cards before inkling playable
		for card in deepcopy(table.play_q):
			if table.list[card].query_bit_pile(qquality = ["playability"],qtype = ["inkling"]):
				table.play_q.remove(card)
				table.play_q.append(card)
		
		for card in deepcopy(table.play_q):
			if table.list[card].query_bit_pile(qquality=["playability"],qtype = ["confirmed"]):
				table.play_q.remove(card)
				table.play_q.appendleft(card)
	
		for card in deepcopy(table.play_q):
			if table.list[card].query_bit_pile(qquality = ["playability"],qspin = ["final"]):
				table.play_q.remove(card)
				table.play_q.appendleft(card)
	 
	def order_discard_q(self,table): #put certainly discardable cards before conventionally discardable before inkling or default discardable
		for card in deepcopy(table.play_q):	
			if table.list[card].query_bit_pile(qquality = ["discardability"],qtype = ["inkling"],qspin = ["neg"]):
				table.play_q.remove(card)
				table.play_q.appendleft(card)
		
		for card in deepcopy(table.play_q):
			if table.list[card].query_bit_pile(qquality = ["discardability"],qtype = ["default"]):
				table.play_q.remove(card)
				table.play_q.appendleft(card)
		
		for card in deepcopy(table.play_q):	
			if table.list[card].query_bit_pile(qquality = ["discardability"],qtype = ["inkling"],qspin = ["pos","final"]):
				table.play_q.remove(card)
				table.play_q.appendleft(card)
		
		for card in deepcopy(table.play_q):	
			if table.list[card].query_bit_pile(qquality=["discardability"],qtype = ["conventional"]):
				table.play_q.remove(card)
				table.play_q.appendleft(card)
			
		for card in deepcopy(table.play_q):
			if table.list[card].query_bit_pile(qquality=["discardability"],qtype = ["confirmed"]):
				table.play_q.remove(card)
				table.play_q.appendleft(card)
			
		for card in deepcopy(table.play_q):
			if table.list[card].query_bit_pile(qquality = ["discardability"],qspin = ["final"]):
				table.play_q.remove(card)
				table.play_q.appendleft(card)
		
	
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
	
	
	
	def will_it_bomb(self,ev): #see Will It Blend with lighters
		pass
	
	
	
	
	def predict_clue(self,ev,table,game):
		#possible ways the clue could go.
		possibilties = ["recently given","playing", "bombing", "protective","dud","multi-play","stalling"]
		
		ikyk_table = ikyk(game, ev.src, ev.tgt)
		
		
		
		for i in range(min(game.variant.playernum - 1,len(game.past_log))): ##Tons of room for improvement here.  This just checks to see if the target received a clue in the last round.
			if game.past_log[-(i+1)].type == "Clue"  and game.past_log[-(i+1)].tgt == ev.tgt:
				return "recently given"
			
		if (table.clued_cards(ev)):
			indicated_card = self.newest(table.clued_cards(ev),table,game)
		
			self.bot.receive_clue(ev,ikyk_table)
		
		
		
			playable_cards = set([x for x in table.list if self.bot.playable(x,game)])
			ikyk_possible_cards = set(self.bot.cards_that_can_be(indicated_card,ikyk_table))
			
			bombing_bool = (indicated_card not in playable_cards) and (ikyk_possible_cards & playable_cards) # (knowing the information the clue gives might lead the tgt to think the indicated card was playable)
				
			protective_bool = (ikyk_table.discard_q[0] in table.critical) # there's also a critical card that's about to be discarded
		
			if table.list[indicated_card].query_bit_pile(qtype=["confirmed"],qvalue=["playable"],qspin=["pos","final"]):
				return "playing"
			elif bombing_bool: 
				return "bombing"
			elif protective_bool: 
				return "protective"
			
		else: 
			pass #this clue is possibly a dud... but with simulation predictions we may see that non-clue clues allow plays to be made
		
		return "dud"
	# playable_cards = set([x for x in table.list if self.playable(x,game)])
		
		# possible_cards = set(self.cards_that_can_be(card,table))
		
		# if possible_cards <= playable_cards:
	
	def interpret_clue(self,ev,table,game):			
		#prepare bools
		protective = False
		playing = False
		stalling = False
		multi_play = False #ohgodohgodohgod
		
		if (table.clued_cards(ev)):
			indicated_card = self.newest(table.clued_cards(ev),table,game)
		
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
			playable_card = self.newest(table.clued_cards(ev),table,game)
			Ibit = Hanabit("conventional","playability","playable","pos",table)
			table.add_bit(Ibit,indicated_card)
			if indicated_card in table.play_q:
				table.play_q.remove(indicated_card)
			table.play_q.appendleft(indicated_card)
			
		if (multi_play):
		#ohgodohgodohgod	
			pass
		
		if(stalling):
		#not sure what this is gonna be, if anything
			pass
		
		
				
				
				
				
				
				
				