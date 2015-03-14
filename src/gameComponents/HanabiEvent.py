__author__ = 'Matthew'




class HanabiEvent(object):
	def __init__(self, src, tgt, type, pos, id, color, number):
		self.src = src
		self.tgt = tgt
		self.type = type  # "Play", "Discard", or "Clue"
		self.pos = pos
		self.id = id
		self.color = color
		self.number = number
		self.touch = []
		self.bomb = None

	def __repr__(self):
		if (self.src == None):
			repstr = "Null Hanabi event"
		else:
			repstr = "{} decided to {} ".format(self.src, self.type)
			if (self.type == "Clue"):
				repstr += "{}".format(self.tgt)
				if (self.number != None):
					repstr += " about {}'s.".format(self.number)
				elif (self.color != None):
					repstr += " about {}'s.".format(self.color)
				else:
					repstr += "... about what, we may never know."
			else:
				repstr += "{}{} (position {}).".format(self.number, self.color, self.pos)
				if self.bomb:
					repstr += " Regrettably."
		return repstr

	def make_clue(self, src, tgt, color, number):
		self.src = src
		self.tgt = tgt
		self.type = "Clue"
		self.color = color
		self.number = number

	def make_play(self, src, pos, id, color, number):
		self.src = src
		self.type = "Play"
		self.id = id
		self.color = color
		self.number = number

	def make_discard(self, src, pos, id, color, number):
		self.src = src
		self.type = "Discard"
		self.id = id
		self.color = color
		self.number = number
