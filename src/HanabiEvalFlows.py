from copy import deepcopy
from HanabiDeductionFlows import *
from HanabiConventionFlows import *
from HanabiClasses import *

class BitTable(object):
	def __init__(self,game,pl=None):  #May want to use id's for some of this?
		self.decktemplate = game.variant.decktemplate
		if pl:
			self.name = pl.name
		else:
			self.name = "None"
		self.list = {card: BitFolder(game,card) for card in game.decks["game_deck"].deck}
		self.location = {location.name: {card: self.list[card] for card in location.deck} 
		                                for deckname, location in game.decks.items()}
		self.known = {card: self.list[card] for card in self.list if self.fixed(card)}
		self.critical = {card: self.list[card]  for card in self.list if (self.only_one(card.color,card.number) and not self.gone(card))}
		self.play_q = deque([])
		if pl:
			self.discard_q = deque(deepcopy(game.decks[pl.name].deck))
		else:
			self.discard_q = deque([])
		#and other pre-organized lists of bit folders
		self.bit_counter = 0
	
	def inc_bit_counter(self):
		self.bit_counter += 1
		
	
	def add_bit(self,tail,card): #pin the tail to a card in the table	
		#only adds it if it isn't contradicted or made redundant by a confirmed bit
		x = self.list[card]
		folder = x.folder
		for bit in folder[tail.quality][tail.value]:
			#should only add bits with "final" spin when one isn't already there
			if bit.spin == "final":
				if tail.spin == "final":
					print("{}: Uh oh. This was already supposed to be final.".format(self.name))
					print(tail)
					return
				elif tail.spin == "neg":
					print("{}: Uh oh. This contradicts some final information.".format(self.name))
					print(tail)
					return
				else:
					print("{}: It was already final that this card is {}.".format(self.name,bit.value))
					return
			
			if bit.type == "confirmed":
				if tail.spin == "pos" and bit.spin == "neg":
					print("{}: Thought for a second that the card WAS {}  when in fact it was already NOT {}.".format(self.name,tail.value,bit.value))
					if tail.type == "inkling":
						print("But it was just an inkling.")
					return
				elif tail.spin == "neg" and bit.spin == "pos":
					print("{}: Thought for a second that the card was NOT {}  when in fact it was already WAS {}.".format(self.name,tail.value,bit.value))
					if tail.type == "inkling":
						print("But it was just an inkling.")
					return
				elif tail.spin == bit.spin:
					if tail.type == "inkling":
						if tail.spin == "pos":
							confirm_string = "IS"
						elif tail.spin == "neg":
							confirm_string = "is NOT"
						print("{}: Inkling already confirmed, this card {} {}.".format(self.name,confirm_string,tail.value))
						return
					if tail.type == "confirmed":
						if tail.spin == "pos":
							confirm_string = "IS"
						elif tail.spin == "neg":
							confirm_string = "is NOT"
						print("{}: I already confirmed that this card {} {}.".format(self.name,confirm_string,tail.value))
						return			
		#DO WE NEED ANY MORE SAFTETIES HERE??
		#Things like being rainbow when it's already negative for another color should be controlled by the game code/logic, not this mechanism
		#By now we feel safe to append, but first we: 
		#remove bits that are conflicting or redundant and less convincing
		if tail.spin == "final": #no other information about that quality is relevant
			x.clear(cquality = tail.quality)
		elif tail.type == "confirmed": #get rid of all inklings of the same value (more sophisticated things will have to be handled by deductions)
			x.clear(ctype ="inkling",cvalue = tail.value)
		x.add_bit(tail)
		self.inc_bit_counter()
	
	def gone(self,card):
		return (card in self.location["Play"] or card in self.location["Discard"])
	
	def dead(self,card):
		card_match = set([x for x in self.list if x.color==card.color and x.number==card.number])
		discarded_cards = set([x for x in self.location["Discard"]])
		return (card_match <= discarded_cards)
	
	def final(self,card,quality):
		for bit in self.list[card].quality_pile[quality]:
			if bit.type=="confirmed" and bit.spin == "final":
				return True
		return False

	def clued_cards(self,ev):
		if (ev.color):
			card_list = [card for card in self.location[ev.tgt] if card.color == ev.color]
		if (ev.number):
			card_list = [card for card in self.location[ev.tgt] if card.number == ev.number]
		return card_list
	
	def played(self,card):
		card_match = set([x for x in self.list if x.color==card.color and x.number==card.number])
		played_cards = set([x for x in self.location["Play"]])
		intersection = card_match & played_cards
		return (len(intersection)==1)
	
	def only_one(self,color,number):  #Needs embellishment, perhaps.  Might be the case that there are zero left.
		total = self.decktemplate.distr[color][number]
		gone_list = [card for card in self.list if (self.gone(card) and card.color == color and card.number == number)]
		number_left = total - len(gone_list)
		if number_left == 1:
			return True
		if number_left == 0:
			print("Just asked if a card that's already gone is the only_one.  You might want to change the list you loop over.")
		return False		
	
	
	def fixed(self,card):
		for bit in self.list[card].pile:
			if bit.spin == "final" and bit.quality == "color":
				for bit in self.list[card].pile:
					if bit.spin == "final" and bit.quality == "number":
						return True
		return False
		
	
	def new_position(self,card,player_name,game):	
		self.list[card].clear(cquality = "position")
		position = game.variant.handsize - game.decks[player_name].deck.index(card)
		Posbit = Hanabit("confirmed","position",position,"final",self)
		self.add_bit(Posbit,card)
		
	def update_positions(self,game):
		for card in self.list:
			in_some_hand = False
			for p in game.players:
				if card in self.location[p.name]:
					in_some_hand = True
					self.new_position(card,p.name,game)
			if (not in_some_hand):
				if self.list[card].query_bit_pile(qquality = ["position"], qspin = ["final"]):
					self.list[card].clear(cquality = "position")
			
			
	
	def new_location(self,card,location_name,game):
		if card in self.location[self.name]: #should already be done when card is played/discarded, but just in case
			if card in self.discard_q:
				self.discard_q.remove(card)
			if card in self.play_q:
				self.play_q.remove(card)
		self.list[card].clear(cquality = "location")
		Lbit = Hanabit("confirmed","location",location_name,"final",self)
		self.add_bit(Lbit,card)
		self.update_location_list(game)
		if location_name == self.name:
			if card not in self.discard_q:
				self.discard_q.append(card)	
			self.add_bit(Hanabit("default","discardability","discardable","default",self),card)
	
	def update_location_list(self,game):
		self.location = {location.name: {card: self.list[card] for card in location.deck} 
		                                for deckname, location in game.decks.items()}
	
	def update_critical_list(self):
		self.critical = {card: self.list[card]  for card in self.list if (self.only_one(card.color,card.number) and not self.gone(card))}
	
	def new_visible(self,card,location,game):
		if not self.final(card,"color"):
			color_bit = Hanabit("confirmed","color",card.color,"final",self)
			self.add_bit(color_bit,card)
		if not self.final(card,"number"):
			number_bit = Hanabit("confirmed","number",card.number,"final",self)
			self.add_bit(number_bit,card)
		self.new_location(card,location,game)
	
	def update_all_lists(self,game):
		self.update_location_list(game)
		self.update_critical_list()
		
	

	
	def make_short_list(self,type,quality,value,spin): #works like the make_pile in BitFolder
		temp_dict = {}
		for card in self.list:
			pile = self.list[card].pile
			for bit in pile:
				bool_type = bit.type in type or 1 in type
				bool_quality = bit.quality in quality or 1 in quality
				bool_value = bit.value in value or 1 in value
				bool_spin = bit.spin in spin or 1 in spin
				if (bool_type and bool_quality and bool_value and bool_spin):
					temp_dict[card] = self.list[card]
					break
		return temp_dict		
	#def make_short_dict(self,type,quality,value,spin,indices): #for cooler looping maybe someday
	
		
	def read_deck(self,name):
		pass		
		
	def tag(self,thing,type,quality,value,spin): 
		bit = Hanabit(type,quality,value,spin,self)
		self.list[thing].folder[quality][value].append(bit)

	def edit_bits(self):
		pass

	def update_knowledge(self):
		pass

class HanabiEvent(object):
	def __init__(self,src,tgt,type,id,color,number):
		self.src = src
		self.tgt = tgt
		self.type = type # "Play", "Discard", or "Clue"
		self.id = id
		self.color = color
		self.number = number
		self.touch = []
		
	def __repr__(self):
		if (self.src == None):
			repstr = "Null Hanabi event"
		else:
			repstr = "{} decided to {} ".format(self.src,self.type)
			if (type == "Clue"):
				repstr += "{}".format(self.tgt)
				if (self.number != None):
					repstr += " about {}'s.".format(self.number)
				elif (self.color != None):
					repstr += " about {}'s.".format(self.color)
				else:
					repstr += "... about what, we may never know."
			else:
				repstr += "{}{}.".format(self.number,self.color)
		return repstr
	
	def make_clue(self,src,tgt,color,number):
		self.src = src
		self.tgt = tgt
		self.type = "Clue"
		self.color = color
		self.number = number

	def make_play(self,src,id,color,number):
		self.src = src
		self.type = "Play"
		self.id = id
		self.color = color
		self.number = number

	def make_discard(self,src,id,color,number):
		self.src = src
		self.type = "Discard"
		self.id = id
		self.color = color
		self.number = number

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
					for num, elt in enumerate(player.trike.tab.discard_q):
						if elt == c:
							qpos = num
					i.bump(1 + len(player.trike.tab.discard_q) - qpos) 
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
		