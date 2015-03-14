__author__ = 'Matthew'



class BitFolder(object):
	def __init__(self, game, card):
		self.types = ["confirmed", "inkling", "conventional", "default"]
		self.qualities = ["color", "number", "location", "playability", "discardability", "position"]
		self.values = {"color": game.colors, "number": game.numbers, "location": game.decks,
					   "playability": ["playable"], "discardability": ["discardable"],
					   "position": [x + 1 for x in range(game.variant.handsize)]}
		self.spins = ["pos", "neg", "final", "default"]
		self.folder = {quality: {value: [] for value in self.values[quality]} for quality in self.qualities}
		self.pile = []
		self.quality_pile = {quality: [] for quality in self.qualities}
		self.value_pile = {value: [] for quality in self.qualities for value in self.values[quality]}

	def __repr__(self):
		return str(self.pile)

	def add_bit(self, bit):
		self.folder[bit.quality][bit.value].append(bit)
		self.pile.append(bit)
		self.quality_pile[bit.quality].append(bit)
		self.value_pile[bit.value].append(bit)

	def remove_bit(self, bit):
		self.folder[bit.quality][bit.value].remove(bit)
		self.pile.remove(bit)
		self.quality_pile[bit.quality].remove(bit)
		self.value_pile[bit.value].remove(bit)

	def query_bit_pile(self, op="conj", qtype=[], qquality=[], qvalue=[],
					   qspin=[]):  # makes list of bits meeting criteria according to operator, input criteria as lists
		temp_list = []
		for bit in self.pile:
			bool_type = bit.type in qtype or not qtype
			bool_quality = bit.quality in qquality or not qquality
			bool_value = bit.value in qvalue or not qvalue
			bool_spin = bit.spin in qspin or not qspin
			if op == "conj":
				if (bool_type and bool_quality and bool_value and bool_spin):
					temp_list.append(bit)
			elif op == "disj":
				if ((bool_type and qtype)
					or (bool_quality and qquality)
					or (bool_value and qvalue)
					or (bool_spin and qspin)):
					temp_list.append(bit)
		return temp_list

	def count_bits(self):  # returns the size of the bit pile
		return len(self.pile)

	def count_bits(self, type, quality, value,
				   spin):  # returns number of bits meeting all criteria, input criteria as lists use [1] for "any"
		return len(self.query_bit_pile(type, quality, value, spin))

	def clear(self, ctype=None, cquality=None, cvalue=None, cspin=None):
		if (ctype and cspin):
			if (cquality):
				for bit in self.quality_pile[cquality][:]:
					if bit.type == ctype and bit.spin == cspin:
						self.remove_bit(bit)
			if (cvalue):
				for bit in self.value_pile[cvalue][:]:
					if bit.type == ctype and bit.spin == cspin:
						self.remove_bit(bit)
			return
		if (ctype):
			if (cquality):
				for bit in self.quality_pile[cquality][:]:
					if bit.type == ctype:
						self.remove_bit(bit)
				return
			if (cvalue):
				for bit in self.value_pile[cvalue][:]:
					if bit.type == ctype:
						self.remove_bit(bit)
				return
		if (cspin):
			if (cquality):
				for bit in self.quality_pile[cquality][:]:
					if bit.spin == cspin:
						self.remove_bit(bit)
				return
			if (cvalue):
				for bit in self.value_pile[cvalue][:]:
					if bit.spin == cspin:
						self.remove_bit(bit)
				return
		if (cvalue):
			for bit in self.value_pile[cvalue][:]:
				self.remove_bit(bit)
			return
		if (cquality):
			for bit in self.quality_pile[cquality][:]:
				self.remove_bit(bit)
			return
