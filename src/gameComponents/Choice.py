__author__ = 'Matthew'




class Choice(object):
	def __init__(self, action=None, tgt=None, color=None, number=None, pos=None):
		self.action = action
		self.tgt = tgt
		self.color = color
		self.number = number
		self.pos = pos
		self.score = 0

	def __repr__(self):
		if self.action == "Clue":
			if self.color:
				return "{} {}: {} eval:{}".format(self.action, self.tgt[:4], self.color, self.score)
			if self.number:
				return "{} {}: {} eval:{}".format(self.action, self.tgt[:4], self.number, self.score)
		else:
			return "{}: pos:{} eval:{}".format(self.action, self.pos, self.score)

	def __lt__(self, other):
		return self.score < other.score

	def bump(self, by):
		self.score = self.score + by
