from copy import deepcopy
from src.gameComponents.HanabiGame import HanabiGame
from src.gameComponents.HanabiGameDeck import HanabiGameDeck

__author__ = 'Matthew'



class HanabiSim(HanabiGame):
	def __init__(self, name, game, N):
		game_copy = deepcopy(game)
		self.deck_copy = deepcopy(game.initial_game_deck)
		super(HanabiSim, self).__init__(name, game_copy.variant, game_copy.con, game.bot, game_copy.total_depth, N)

	def add_player(self, dude):
		self.players.append(dude)

	def set_game_deck(self):
		self.add_card_list(HanabiGameDeck("card_list", self.variant, self.variant.decktemplate))
		game_deck = self.deck_copy
		initial_game_deck = deepcopy(game_deck)
		self.add_initial_game_deck(initial_game_deck)
		self.add_deck(game_deck)

	def initial_player_order(self, player_name_list):
		player_list = []
		for name in player_name_list:
			player_list.append(HanabiSimNPC(name, self, self.depth))

		for i in range(len(player_list)):
			self.add_player(player_list.pop(0))  # fed in in order of the real game
		self.players_initial = deepcopy(self.players)
		for dude in self.players:
			dude.initialize_trike(self)