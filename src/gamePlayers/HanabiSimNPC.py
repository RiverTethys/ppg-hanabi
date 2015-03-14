from src.gamePlayers.HanabiNPC import HanabiNPC

__author__ = 'Matthew'



class HanabiSimNPC(HanabiNPC):
	def __init__(self, name, game, N):
		HanabiNPC.__init__(self, name, game)
		self.depth = N
		self.fref = ".\\{}depth{}.hanabidata".format(name, self.depth)

	def im_a_dummy(self):
		if self.depth == self.game.total_depth:
			return True
		return False

	def im_with_stupid(self):
		if self.depth == self.game.total_depth - 1:
			return True
		return False



