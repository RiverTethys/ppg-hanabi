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
	
	
	
	def cards_that_can_be(self,card,table): #for the given card, return the _SET_ of cards it could be
		if table.fixed(card):
			return set([card])
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
		if table.bool_query(qcard = card,qtype="confirmed", qquality = "playability",qspin = "final"):
			return
		playable_cards = set([x for x in table.list if self.playable(x,game)])
		
		possible_cards = set(self.cards_that_can_be(card,table))
		
		if possible_cards <= playable_cards:
			if table.bool_query(qcard = card, qvalue = 5,qspin = "final"):
				Pbit = Hanabit("confirmed","playability","playable","final",table)
			else:
				Pbit = Hanabit("confirmed","playability","playable","pos",table)
			table.add_bit(Pbit,card)
			if card in table.location[table.name]:
				if card in table.discard_q:
					table.discard_q.remove(card)
				if card not in table.play_q:
					table.play_q.appendleft(card)
				if card in table.play_q:
					table.play_q.appendleft(table.play_q.pop(card.index()))
		else:
			if table.bool_query(qcard= card,qtype ="confirmed",qvalue = "playable",qspin="pos"):
				Pbit = Hanabit("confirmed","playability","playable","pos",table)
				table.list[card].remove_bit(Pbit)
			if card in table.location[table.name]:
				if card in table.play_q:
					table.play_q.remove(card)  #Our first set of bot will be super cautious
		
	def deduce_discardability(self,card,table):
		if table.bool_query(qcard = card, qquality = "discardability",qspin = "final"):
			return
		known_color = table.list[card].make_bit_pile(["confirmed"],["color"],[1],["final","pos"])
		known_number = table.list[card].make_bit_pile(["confirmed"],["number"],[1],["final","pos"])
		#print(known_color)
		#print(known_number)
		if len(known_color) == 1 and len(known_number) == 1:
			#if it has already been played or if it's already a dead card, confirmed, trash, final		
			if table.played(card) or table.dead(card):
				Dbit = Hanabit("confirmed","discardability","trash","final",table)
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
			#if it is not the only one, confirmed, discardable, pos
			else:
				Dbit=Hanabit("confirmed","discardability","discardable","pos",table)
				if card in table.location[table.name]:
					if card not in table.discard_q:
						table.discard_q.append(card)
		
		## Could use some additional work here, for when the color and number are not both known
		
			table.add_bit(Dbit,card)
	
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
				table.add_bit(FBit,card)
				return
		#deduce negative information
		known_number_list = [bit.value for bit in bit_folder.quality_pile["number"] if bit.type == "confirmed" and bit.spin == "final"]
		if len(known_number_list) == 1:
			known_number = known_number_list[0]
			for color in bit_folder.values["color"]:
				if self.all_known(color,known_number,table):
					Nbit = Hanabit("confirmed","color",color,"neg",table)
					table.add_bit(NBit,card)
		#check for deduction by negative information/process of elimination
		x = self.negative_info_elim(bit_folder.quality_pile["color"],bit_folder.values["color"])
		if x[0]:
			Fbit = Hanabit("confirmed",quality,x[1],"final",table)
			table.add_bit(FBit,card)
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
			for card in table.location[ev.tgt]:
				if card.color == ev.color:
					Fbit = Hanabit("confirmed","color",ev.color,"final",table)
					table.add_bit(Fbit,card)
				else:
					Nbit = Hanabit("confirmed","color",ev.color,"neg",table)
					table.add_bit(Nbit,card)
		if ev.number:
			for card in table.location[ev.tgt]:
				if card.number == ev.number:
					Fbit = Hanabit("confirmed","number",ev.number,"final",table)
					table.add_bit(Fbit,card)
				else:
					Nbit = Hanabit("confirmed","number",ev.number,"neg",table)
					table.add_bit(Nbit,card)
		
	def interpret_clue(self,ev):
		pass

		
class Hanabit(object): # a single piece of information
	def __init__(self,knowledgeType,quality,value,spin,tab):
		self.tab = tab
		self.id = tab.bit_counter
		self.type = knowledgeType #confirmed,inkling,etc.
		self.quality = quality #color,number,protected, playable, discardable, etc.
		self.value = value #'R',3,True,etc.
		self.spin = spin #pos,neg,final (it is this thing to the exclusion of all others)	
		
	def __repr__(self):
		if self.quality == "location":
			output_str = self.quality[0:3]+":"+self.value
		elif self.quality == "number" or self.quality == "color":
			output_str = self.type[0:1].upper()+self.spin[0:1].upper()+" "+str(self.value)
		else:
			type_str = self.type[0:1].upper()
			quality_str = self.quality[0:3]
			value_str = str(self.value)
			spin_str = self.spin[0:1].upper()
			output_str = type_str+spin_str+" "+quality_str+":"+value_str
		return output_str		
	
	def __eq__(self,other):
		return (self.type == other.type and self.quality == other.quality and self.value == other.value and self.spin==other.spin)
	
	def __hash__(self):
		return hash((self.tab,self.id))	
# def all_known(self,value,table):
	# if value in self.decktemplate.colors:
		# value_list = {card:table.list[card] for card in table.list if card.color == value}
	# if value in self.decktemplate.numbers:
		# value_list = {card:table.list[card] for card in table.list if card.num == value}
	# for card in value_list:
		# if card not in table.known:
			# return False
	# return True
			
			
# def deduce_colors(self,game): ###  RAINBOW EDITION
	# for card in self.hand.c:
		# #Check if this is already done
		# for color in card.bits["color"]:
				# for bit in card.bits["color"][color]:
					# if bit.spin == "final" and bit.type == "confirmed":
						# continue
		# #If there is confirmed multiple color info, then it must be rainbow
		# if self.count_bits(self,card,"confirmed","color","any","pos") > 2:
			# Hbit=Hanabit("confirmed","color","H","final")
			# self.add_bit(HBit,card)
			# continue 
		# #If there is confirmed single color info, then rainbow has been eliminated and that info must be final.
		# if self.count_bits(self,card,"confirmed","color","any","pos") == 1:
			# for color in card.bits["color"]:
				# for bit in card.bits["color"][color]:
					# if bit.type == "confirmed":
						# Cbit = Hanabit("confirmed","color",bit.value,"final")
						# self.add_bit(CBit,card)
						# continue
		# #We can also deduce color by stacking negative information
		# color_set = set(deepcopy(game.colors))
		# #Continuing with this, we can also check to see what cards it cannot be given visible cards
		
		# #what else do we need here?
		# return
					
			
# class BitFolder(object):
	# def __init__(self,game,card):
		# self.qualities = ["color","num"]
		# self.values = {"color":game.colors,"num":game.numbers}
		# self.folder = {quality:{value:[] for value in self.values[quality]} for quality in self.qualities}		

		
# class BitTable(object):
	# def __init__(self,game):  #May want to use id's for some of this?
		# self.list = {card: BitFolder(game,card) for card in game.card_list}
		# self.location = {location.name: {card: self.list[card] for card in location.deck} for location in game.decks}
		# visible_cards = {}
		# #figure out self.visible
		# self.critical = {card: self.list[card]  for card in self. if self.only_one(card)}
		# #and other pre-organized list of bit folders
	# def only_one(self,card):
		# pass
	# def update_all_lists(self):
		# pass
	# def update_critical(self):
		# pass
	# def update_location(self):
		# pass
	# def update_short_list(self,short_list,criteria):
		# pass
	# def make_short_list(self,criteria):
		# pass
		
				



