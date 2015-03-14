from src.gameBits.BitTable import BitTable

__author__ = 'Matthew'


class Tricorder(object):
	def __init__(self, game, player):
		self.name = player.name
		self.tab = BitTable(game, pl=player.name)
		self.bot = game.bot
		self.con = game.con

	def simulate(self, game, EventList, n):
		decision = self.decide(game)
		game.take_action(decision)
		EventList.append(decision)
		if n == 0:
			return
		else:
			return self.simulate(game, EventList, n - 1)

	def set_conventions(self, conventions):
		self.con = conventions

	def run_sim(self, game, action, n):
		CurrentState = game.past_log
		game.take_action(action)
		EventList = [action]
		self.simulate(game, EventList, n)
		game.reset(CurrentState)
		return EventList

	def update_table(self, game):
		self.tab.update_all_lists(game)
		self.bot.update_playability(self.tab, game)
		self.bot.update_discardability(self.tab)
		self.bot.update_color(self.tab)
		self.bot.update_number(self.tab)


	def decide(self):
		pass
