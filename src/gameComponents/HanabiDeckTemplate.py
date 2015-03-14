__author__ = 'Matthew'



class HanabiDeckTemplate(object):
	def __init__(self, colors, numbers, distr):
		self.colors = colors
		self.numbers = numbers
		self.distr = distr

	def __len__(self):
		size = 0
		for color in self.colors:
			for num in self.distr[color]:
				size += num
		return size
