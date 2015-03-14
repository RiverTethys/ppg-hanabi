from collections import deque
from copy import deepcopy
from src.gameBits.BitFolder import BitFolder
from src.gameBits.Hanabit import Hanabit

__author__ = 'Matthew'



class BitTable(object):
	def __init__(self, game, pl=None):  # May want to use id's for some of this?
		self.decktemplate = game.variant.decktemplate
		if pl:
			self.name = pl
		else:
			self.name = "None"
		# print (game)
		# print (game.card_list.deck)
		self.list = {card: BitFolder(game, card) for card in game.card_list.deck}
		self.current_list = self.list

		# for debugging
		#	print("{} BitTable list:".format(self.name))
		#	r = ""
		#	i = 0
		#	for elt in self.list:
		#		r = r + "{}: {}  ".format(elt,self.list[elt])
		#		i += 1
		#		if (i % 8 == 0):
		#			r = r + "\n"
		#	if not r.replace("\n",""):
		#		print("Empty.\n")
		#	else:
		#		print(r)
		#
		#	for deckname, location in game.decks.items():
		#		print("Deck: {}".format(deckname))
		#		r = ""
		#		i = 0
		#		for card in location.deck:
		#			r = r + "{}: {}  ".format(i,card)
		#			i += 1
		#			if (i % 8 == 0):
		#				r = r + "\n"
		#		if not r.replace("\n",""):
		#			print("Empty.\n")
		#		else:
		#			print(r)

		self.location = {location.name: {card: self.list[card] for card in location.deck}
						 for deckname, location in game.decks.items()}
		self.known = {card: self.list[card] for card in self.list if self.fixed(card)}
		self.critical = {card: self.list[card] for card in self.list if self.only_one(card.color, card.number)}
		self.play_q = deque([])
		if pl:
			self.discard_q = deque(deepcopy(game.decks[pl].deck))
		else:
			self.discard_q = deque([])
		#and other pre-organized lists of bit folders
		self.bit_counter = 0

	def inc_bit_counter(self):
		self.bit_counter += 1


	def add_bit(self, tail, card):  # pin the tail to a card in the table
		# only adds it if it isn't contradicted or made redundant by a confirmed bit
		x = self.list[card]
		folder = x.folder

		for bit in folder[tail.quality][tail.value]:
			# should only add bits with "final" spin when one isn't already there
			if bit.spin == "final":
				if tail.spin == "final":
					print("{}: Uh oh. This was already supposed to be final.".format(self.name))
					print(tail)
					return
				elif tail.spin == "neg":
					print("{}: Uh oh. This contradicts some final information.".format(self.name))
					print(tail)
					#print(folder)
					#takeonefortheteam
					return

				else:
					print("{}: It was already final that {} is {}.".format(self.name, card, bit.value))
					return

			if bit.type == "confirmed":
				if tail.spin == "pos" and bit.spin == "neg":
					if (tail.quality == "color" or tail.quality == "number"):
						print("{}: Thought for a second that {} WAS {}  when in fact it was already NOT {}.".format(
							self.name, card, tail.value, bit.value))
						if tail.type == "inkling":
							print("But it was just an inkling.")
						return
					else:
						x.remove_bit(bit)
						print("This is fixed ish, but we should check that these deductions switch for a reason")
				elif tail.spin == "neg" and bit.spin == "pos":
					if (tail.quality == "color" or tail.quality == "number"):
						print("{}: Thought for a second that {} was NOT {}  when in fact it was already WAS {}.".format(
							self.name, card, tail.value, bit.value))
						if tail.type == "inkling":
							print("But it was just an inkling.")
						return
					else:
						x.remove_bit(bit)
						print("This is fixed ish, but we should check that these deductions switch for a reason")
				elif tail.spin == bit.spin:
					if tail.type == "inkling":
						if tail.spin == "pos":
							confirm_string = "IS"
						elif tail.spin == "neg":
							confirm_string = "is NOT"
						print("{}: Inkling already confirmed, {} {} {}.".format(self.name, card, confirm_string,
																				tail.value))
						return
					if tail.type == "confirmed":
						if tail.spin == "pos":
							confirm_string = "IS"
						elif tail.spin == "neg":
							confirm_string = "is NOT"
						print("{}: I already confirmed that {} {} {}.".format(self.name, card, confirm_string,
																			  tail.value))
						print(folder)
						#breakforme
						return
		# DO WE NEED ANY MORE SAFETIES HERE??
		#Things like being rainbow when it's already negative for another color should be controlled by the game code/logic, not this mechanism
		#By now we feel safe to append, but first we:
		#remove bits that are conflicting or redundant and less convincing
		if tail.spin == "final":  #no other information about that quality is relevant
			x.clear(cquality=tail.quality)
		elif tail.type == "confirmed":  #get rid of all inklings of the same value (more sophisticated things will have to be handled by deductions)
			x.clear(ctype="inkling", cvalue=tail.value)
		x.add_bit(tail)
		self.inc_bit_counter()

	def gone(self, card):
		return (card in self.location["Play"] or card in self.location["Discard"])

	def dead(self, card):
		card_match = set([x for x in self.list if x.color == card.color and x.number == card.number])
		discarded_cards = set([x for x in self.location["Discard"]])
		return (card_match <= discarded_cards)

	def final(self, card, quality):
		return self.list[card].query_bit_pile(qtype=["confirmed"], qquality=[quality], qspin=["final"])

	def clued_cards(self, ev):
		if (ev.color):
			card_list = [card for card in self.location[ev.tgt] if card.color == ev.color]
		if (ev.number):
			card_list = [card for card in self.location[ev.tgt] if card.number == ev.number]
		return card_list

	def played(self, card):
		card_match = set([x for x in self.list if x.color == card.color and x.number == card.number])
		played_cards = set([x for x in self.location["Play"]])
		return card_match & played_cards

	def only_one(self, color, number):  # Needs embellishment, perhaps.  Might be the case that there are zero left.
		total = self.decktemplate.distr[color][number]
		gone_list = [card for card in self.list if (self.gone(card) and card.color == color and card.number == number)]
		number_left = total - len(gone_list)
		if number_left == 1:
			return True
		return False

	def fixed(self, card):
		if self.final(card, "color") and self.final(card, "number"):
			return True
		return False


	def new_position(self, card, player_name, game):
		self.list[card].clear(cquality="position")
		position = game.variant.handsize - game.decks[player_name].deck.index(card)
		Posbit = Hanabit("confirmed", "position", position, "final", self)
		self.add_bit(Posbit, card)

	def update_positions(self, game):
		for card in self.list:
			in_some_hand = False
			for p in game.players:
				if card in self.location[p.name]:
					in_some_hand = True
					self.new_position(card, p.name, game)
			if (not in_some_hand):
				if self.final(card, "position"):
					self.list[card].clear(cquality="position")

	def new_location(self, card, location_name, game):
		if card in self.location[self.name]:  # should already be done when card is played/discarded, but just in case
			if card in self.discard_q:
				self.discard_q.remove(card)
			if card in self.play_q:
				self.play_q.remove(card)
		self.list[card].clear(cquality="location")
		Lbit = Hanabit("confirmed", "location", location_name, "final", self)
		self.add_bit(Lbit, card)
		self.update_location_list(game)
		if location_name == self.name:
			if card not in self.discard_q:
				self.discard_q.append(card)
			self.add_bit(Hanabit("default", "discardability", "discardable", "default", self), card)

	def new_visible(self, card, location, game):
		if not self.final(card, "color"):
			color_bit = Hanabit("confirmed", "color", card.color, "final", self)
			self.add_bit(color_bit, card)
		if not self.final(card, "number"):
			number_bit = Hanabit("confirmed", "number", card.number, "final", self)
			self.add_bit(number_bit, card)
		self.new_location(card, location, game)

	def update_location_list(self, game):
		self.location = {location.name: {card: self.list[card] for card in location.deck}
						 for deckname, location in game.decks.items()}

	def update_critical_list(self):
		self.critical = {card: self.list[card] for card in self.list if
						 ( not self.gone(card) and self.only_one(card.color, card.number))}

	def update_known_list(self):
		self.known = {card: self.list[card] for card in self.list if self.fixed(card)}

	def update_all_lists(self, game):
		self.update_location_list(game)
		self.update_positions(game)
		self.update_critical_list()
		self.update_known_list()

	def make_short_list(self, type, quality, value, spin):  # works like the make_pile in BitFolder
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

	# def make_short_dict(self,type,quality,value,spin,indices): #for cooler looping maybe someday

