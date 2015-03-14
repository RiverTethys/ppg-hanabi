from src.gameComponents.HanabiUtilityMethods import event_from_choice, eval_flow
from src.gamePlayers.Player import Player

__author__ = 'Matthew'




class HanabiNPC(Player):
	def __init__(self, name, game):
		Player.__init__(self, name, game)

	def decision(self, game):
		return event_from_choice(eval_flow(self, game).pop(), self, game)

	def analysis(self):
		pass