from HanabiClasses import *
from copy import deepcopy

def main_flow(player,game):
	pass
#Bit arguments def __init__(self,publicBool,ownerName,knowledgeType,quality,value,spin):
#and 	def count_bits(self,searcher,thing,type,quality,value,spin): 

class DeductionBot(object):
	def __init__(self,variant):
		self.decktemplate = variant.decktemplate
		self.players = []

	def set_players(self,players):
		self.players = deepcopy(players)
	
	def playable(self,card,game):
		for x in game.play.deck:
			if (x.color == card.color and x.number == card.number):
				return False
		if card.number == 1:
			return True
		for x in game.play.deck:
			if (x.color == card.color and x.number == (card.number - 1) ):
				return True
		return False
	
	def turns_since_clued(self,card,game): #returns integer number of turns since _last_ clued about a given card. Minimum 1. 0 means never.
		time_indices = []
		for i, ev in enumerate(game.past_log):
			if (ev.type == "Clue" and card in ev.touch):
				time_indices.append(i)
		if time_indices:
			return len(game.past_log) - time_indices[-1]
		else:
			return 0
	
	
	
	def cards_that_can_be(self,card,table): #for the given card, return the LIST of cards it could be
		if table.fixed(card):
			return [card]
		card_list = [x for x in table.list if not table.gone(x)]
		for bit in table.list[card].pile:   #eliminate based on information about "card"
			if bit.quality == "color":
				if bit.spin == "pos"  or bit.spin == "final":
					for x in card_list[:]:
						if x.color != bit.value:
							card_list.remove(x)
				if bit.spin == "neg":
					for x in card_list[:]:
						if x.color == bit.value:
							card_list.remove(x)
			if bit.quality == "number":
				if bit.spin == "pos"  or bit.spin == "final":
					for x in card_list[:]:
						if x.number != bit.value:
							card_list.remove(x)
				if bit.spin == "neg":
					for x in card_list[:]:
						if x.number == bit.value:
							card_list.remove(x)
			#Note that elimination based on cards seen around the table has been covered by other deductions (unless narrowing the number of possible cards is desired)
		return card_list
		
	def cards_that_cant_be(self,card,table): # return the _SET_ of cards that this card cannot be
		card_list = set([x for x in table.list])
		complement = set(self.cards_that_can_be(card,table))
		return list(card_list - complement)
		
		
	
	
	def deduce_playability(self,card,table,game):
		if table.final(card,"playability"):
			return
		playable_cards = set([x for x in table.list if self.playable(x,game)])
		possible_cards = set(self.cards_that_can_be(card,table))
		
		
		if possible_cards <= playable_cards:
			if table.list[card].query_bit_pile( qvalue = [5],qspin = ["final"]):
				Pbit = Hanabit("confirmed","playability","playable","final",table)
			else:
				Pbit = Hanabit("confirmed","playability","playable","pos",table)
			if not table.list[card].query_bit_pile(qtype=["confirmed"],qquality=["playability"],qspin=["pos","final"]):
				table.add_bit(Pbit,card)
			table.list[card].clear(cquality="discardability")
			if card in table.location[table.name]:
				if card in table.discard_q:
					table.discard_q.remove(card)
				if card in table.play_q:
					table.play_q.remove(card)
				table.play_q.appendleft(card)
		else:
			if table.list[card].query_bit_pile(qtype =["confirmed"],qvalue = ["playable"],qspin=["pos"]):
				Pbit = Hanabit("confirmed","playability","playable","pos",table)
				table.list[card].remove_bit(Pbit)
			if card in table.location[table.name]:
				if card in table.play_q:
					table.play_q.remove(card)  #Our first set of bot will be super cautious
		
	def deduce_discardability(self,card,table):
		if table.list[card].query_bit_pile(qtype = ["confirmed"],qquality = ["discardability"],qspin = ["final","neg"]):
			return
		known_color = table.list[card].query_bit_pile(qtype =["confirmed"],qquality = ["color"],qspin = ["final","pos"])
		known_number = table.list[card].query_bit_pile(qtype = ["confirmed"],qquality = ["number"],qspin = ["final","pos"])
		#print(known_color)
		#print(known_number)
		if len(known_color) == 1 and len(known_number) == 1:
			#if it has already been played or if it's already a dead card, confirmed, trash, final		
			if table.played(card) or table.dead(card):
				Dbit = Hanabit("confirmed","discardability","discardable","final",table)
				table.add_bit(Dbit,card)
				if card in table.location[table.name]:
					if card in table.play_q:
						table.play_q.remove(card)
					if card not in table.discard_q:
						table.discard_q.appendleft(card)
				return
			#if it is the only one, confirmed, discardable, neg   (or maybe confirmed, not discardable, final)
			if table.only_one(known_color[0].value,known_number[0].value):
				Dbit=Hanabit("confirmed","discardability","discardable","neg",table)
				if card in table.location[table.name]:
					if card in table.discard_q:
						table.discard_q.remove(card)
				if not table.list[card].query_bit_pile(qtype=["confirmed"],qquality= ["discardability"],qspin = ["neg"]):
					table.add_bit(Dbit,card)
			#if it is not the only one, confirmed, discardable, pos
			elif not table.list[card].query_bit_pile(qtype = ["confirmed"],qquality=["discardability"],qspin=["pos"]):
				Dbit=Hanabit("confirmed","discardability","discardable","pos",table)
				if card in table.location[table.name]:
					if card not in table.discard_q:
						table.discard_q.append(card)
				table.add_bit(Dbit,card)
		else: ## Could use some additional work here, for when the color and number are not both known
			possible_cards = set(self.cards_that_can_be(card,table))
			played_cards = set([x for x in table.list if table.played(card)])
			dead_cards = set([x for x in table.list if table.dead(card)])
			discardable_cards = played_cards | dead_cards
			if possible_cards <= discardable_cards:
				Dbit = Hanabit("confirmed","discardability","discardable","final",table)
				if not table.final(card,"discardability"):
					table.add_bit(Dbit,card)
				table.list[card].clear(cquality="playability")
				if card in table.location[table.name]:
					if card in table.play_q:
						table.play_q.remove(card)
					if card in table.discard_q:
						table.discard_q.remove(card)
					table.discard_q.appendleft(card)
	
	def update_playability(self,table,game):
		for card in table.list:
			self.deduce_playability(card,table,game)
	
	def update_discardability(self,table):
		for card in table.list:
			self.deduce_discardability(card,table)
	
	def negative_info_elim(self,bit_pile,value_list): # if successful return [True,remaining value]  If unsuccessful return [False]
		#print(bit_pile)
		#print(value_list)
		temp = deepcopy(value_list)
		for bit in bit_pile:
			if bit.type == "confirmed"  and bit.spin == "neg":
				temp.remove(bit.value)
		if len(temp)==1:
			return [True,temp[0]]
		return [False]
				
	
	def all_known(self,color,number,table):
		card_list = {}
		for card in table.list:
			if card.color == color and card.number == number:
				card_list[card] = table.list[card]
		for card in card_list:
			if card not in table.known:
				return False
		return True
		
	def deduce_color(self,card,table):
		bit_folder = table.list[card]	
		for bit in bit_folder.quality_pile["color"]: 
			if bit.spin == "final" and bit.type == "confirmed": #check if already done
				return
			if bit.spin =="pos" and bit.type == "confirmed": # check if there's a confirmed positive
				Fbit = Hanabit("confirmed","color",bit.value,"final",table)
				table.add_bit(Fbit,card)
				return
		#deduce negative information
		known_number_list = [bit.value for bit in bit_folder.quality_pile["number"] if bit.type == "confirmed" and bit.spin == "final"]
		if len(known_number_list) == 1:
			known_number = known_number_list[0]
			for color in bit_folder.values["color"]:
				if self.all_known(color,known_number,table):
					Nbit = Hanabit("confirmed","color",color,"neg",table)
					table.add_bit(Nbit,card)
		#check for deduction by negative information/process of elimination
		x = self.negative_info_elim(bit_folder.quality_pile["color"],bit_folder.values["color"])
		if x[0]:
			Fbit = Hanabit("confirmed","color",x[1],"final",table)
			table.add_bit(Fbit,card)
			return
	
	def deduce_number(self,card,table):
		bit_folder = table.list[card]	
		for bit in bit_folder.quality_pile["number"]: 
			if bit.spin == "final" and bit.type == "confirmed": #check if already done
				return
			if bit.spin =="pos" and bit.type == "confirmed": # check if there's a confirmed positive
				Fbit = Hanabit("confirmed","number",bit.value,"final",table)
				table.add_bit(FBit,card)
				return
		#deduce negative information
		known_color_list = [bit.value for bit in bit_folder.quality_pile["color"] if bit.type == "confirmed" and  bit.spin == "final"]
		if len(known_color_list) == 1:
			known_color = known_color_list[0]
			for number in bit_folder.values["number"]:
				if self.all_known(known_color,number,table):
					Nbit = Hanabit("confirmed","number",number,"neg",table)
					table.add_bit(Nbit,card)		
		#check for deduction by negative information/process of elimination
		x = self.negative_info_elim(bit_folder.quality_pile["number"],bit_folder.values["number"])
		if x[0]:
			Fbit = Hanabit("confirmed","number",x[1],"final",table)
			table.add_bit(Fbit,card)
			return
	
	def deduce_color_list(self,card_list,table):
		for card in card_list:
			self.deduce_color(card,table)
	
	def deduce_number_list(self,card_list,table):
		for card in card_list:
			self.deduce_number(card,table)

	def update_color(self,table):
		for card in table.location[table.name]:
			self.deduce_color(card,table)
		
	def update_number(self,table):
		for card in table.location[table.name]:
			self.deduce_number(card,table)
		
		
	def receive_clue(self,ev,table):
		if ev.color:
			for card in set(ev.touch).intersection(set(table.location[ev.tgt])):
				if card.color == ev.color and not table.list[card].query_bit_pile(qtype = ["confirmed"],qspin = ["final"], qvalue = [ev.color]):
					Fbit = Hanabit("confirmed","color",ev.color,"final",table)
					table.add_bit(Fbit,card)
				elif not table.list[card].query_bit_pile(qtype = ["confirmed"],qspin = ["neg"], qvalue = [ev.color]):
					Nbit = Hanabit("confirmed","color",ev.color,"neg",table)
					table.add_bit(Nbit,card)
		if ev.number:
			for card in set(ev.touch).intersection(set(table.location[ev.tgt])):
				if card.number == ev.number and not table.list[card].query_bit_pile(qtype = ["confirmed"],qspin=["final"],qvalue = [ev.number]):
					Fbit = Hanabit("confirmed","number",ev.number,"final",table)
					table.add_bit(Fbit,card)
				elif not table.list[card].query_bit_pile(qtype = ["confirmed"],qspin=["neg"],qvalue = [ev.number]):
					Nbit = Hanabit("confirmed","number",ev.number,"neg",table)
					table.add_bit(Nbit,card)
		
	def interpret_clue(self,ev):
		pass

				



