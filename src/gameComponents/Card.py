__author__ = 'Matthew'


class Card(object):
	def __init__(self, id, color, number):
		self.id = id
		self.number = number
		self.color = color

	def __repr__(self):
		# return "({})".format(self.id) + str(self.number) + self.color + " "
		return str(self.number) + self.color + " "

	def __str__(self):
		# return "({})".format(self.id) + str(self.number) + self.color + " "
		return str(self.number) + self.color + " "

	def __eq__(self, other):
		return self.id == other.id and self.color == other.color and self.number == other.number

	def __hash__(self):
		return hash(self.id)