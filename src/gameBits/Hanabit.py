__author__ = 'Matthew'



class Hanabit(object):  # a single piece of information
	def __init__(self, knowledgeType, quality, value, spin, tab):
		self.tab = tab
		self.id = tab.bit_counter
		self.type = knowledgeType  # confirmed,inkling,etc.
		self.quality = quality  # color,number,protected, playable, discardable, etc.
		self.value = value  # 'R',3,True,etc.
		self.spin = spin  # pos,neg,final (it is this thing to the exclusion of all others)

	def __repr__(self):
		if self.quality == "location":
			output_str = self.quality[0:3] + ":" + self.value
		elif self.quality == "number" or self.quality == "color":
			output_str = self.type[0:1].upper() + self.spin[0:1].upper() + " " + str(self.value)
		else:
			type_str = self.type[0:1].upper()
			quality_str = self.quality[0:3]
			value_str = str(self.value)
			spin_str = self.spin[0:1].upper()
			output_str = type_str + spin_str + " " + quality_str + ":" + value_str
		return output_str

	def __eq__(self, other):
		return (
			self.type == other.type and self.quality == other.quality and self.value == other.value and self.spin == other.spin)

	def __hash__(self):
		return hash((self.tab, self.id))
