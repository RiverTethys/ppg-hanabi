from collections import deque
from copy import deepcopy
from src.gameComponents.Card import Card
from src.gameComponents.HanabiEvent import HanabiEvent
from src.gameComponents.HanabiGameDeck import HanabiGameDeck
from src.gameComponents.HanabiStacks import HanabiStacks
from src.gamePlayers.HanabiNPC import HanabiNPC
from src.gamePlayers.Player import Player

__author__ = 'Matthew'



class HanabiGame(object):
	def __init__(self, name, variant, conventions, deduction_bot, total_depth, depth):
		self.name = name
		self.total_depth = total_depth
		self.variant = variant
		self.colors = variant.colors
		self.numbers = variant.numbers
		self.distr = variant.decktemplate.distr
		self.players = deque([])
		self.players_initial = []
		self.rules = variant.rules
		self.play = []
		self.discard = []
		self.clocks = variant.clocks
		self.MAX_CLOCKS = variant.clocks
		self.bombs = variant.bombs
		self.MAX_BOMBS = variant.bombs
		self.fref = ".\\{}.hanabilog".format(name)
		self.con = conventions
		self.bot = deduction_bot
		self.defeat = False
		self.victory = False
		self.final_countdown = 0
		self.card_list = {}
		self.initial_game_deck = {}
		self.decks = {}
		self.depth = depth
		self.nextgame = []

	def __repr__(self):
		return self.name

	def set_game_deck(self, deckfile=None):
		self.add_card_list(HanabiGameDeck("card_list", self.variant, self.variant.decktemplate, deckfile=deckfile))
		game_deck = HanabiGameDeck("game_deck", self.variant, self.variant.decktemplate, deckfile=deckfile)
		if self.depth == 0:
			game_deck.print_distr()
		if not deckfile:
			game_deck.shuffle()

		initial_game_deck = deepcopy(game_deck)
		self.add_initial_game_deck(initial_game_deck)
		self.add_deck(game_deck)

	def set_stacks(self):
		self.add_deck(HanabiStacks("Play", self.variant, self.variant.stackstemplate))
		self.add_deck(HanabiStacks("Discard", self.variant, self.variant.stackstemplate))
		self.play = self.decks["Play"]
		self.discard = self.decks["Discard"]

	def add_deck(self, deck):
		self.decks[deck.name] = deck

	def add_initial_game_deck(self, initial_game_deck):
		self.initial_game_deck = initial_game_deck

	def add_card_list(self, card_list):
		self.card_list = card_list

	def set_game_log(self):
		# calculate maximum length of log
		NUM_PLAYS_TO_WIN = len(self.colors) * len(self.numbers)
		NUM_OF_FIVES = len(self.colors)
		INITIAL_CLOCKS = self.clocks
		INITIAL_DECK_SIZE = len(self.decks["game_deck"])
		NUM_PLAYERS = len(self.players)
		MAX_TURNS = NUM_PLAYS_TO_WIN + INITIAL_CLOCKS + NUM_OF_FIVES + 2 * (
			INITIAL_DECK_SIZE - NUM_PLAYS_TO_WIN) - 1 + NUM_PLAYERS

		# initialize Future Log
		self.future_log = deque([HanabiEvent(None, None, None, None, None, None, None) for x in range(MAX_TURNS)])
		self.past_log = []

	def set_nextgame(self, nextgame):
		self.nextgame = nextgame

	def set_nextplayers(self, nextgame):
		for seat, dude in enumerate(self.players):
			if seat == len(self.players) - 1:
				dude.set_nextplayer(self.nextgame.players[0])
			else:
				dude.set_nextplayer(self.nextgame.players[seat + 1])

	def set_conventions(self, conventions):
		self.con = conventions
		for p in self.players:
			p.trike.set_conventions(self.con)

	def inc_clocks(self):
		self.clocks += 1

	def dec_clocks(self):
		self.clocks -= 1

	def bomb(self):
		self.bombs -= 1
		if (self.bombs == 0):
			self.defeat = True

	def inc_fc(self):
		self.final_countdown += 1

	def draw_card(self, deckname):
		return self.decks[deckname].draw()

	# table update occurs in Player

	def play_card(self, card, player):
		if self.bot.playable(card, self):
			for handcard in self.decks[player.name].deck:
				if handcard == card:
					idx = self.decks[player.name].deck.index(handcard)
					break
			self.play.add(self.decks[player.name].deck.pop(idx))
			# update tables
			for dude in self.players:
				if dude.name != player.name:
					dude.trike.tab.new_location(card, "Play", self)
			player.trike.tab.new_visible(card, "Play", self)

			if len(self.play) == 25:
				self.victory = True
			return True
		else:
			self.bomb()
			self.discard_card(card, player)
			return False

	def discard_card(self, card, player):
		for handcard in self.decks[player.name].deck:
			if handcard == card:
				idx = self.decks[player.name].deck.index(handcard)
				break
		self.discard.add(self.decks[player.name].deck.pop(idx))
		# update tables
		for dude in self.players:
			if dude.name != player.name:
				dude.trike.tab.new_location(card, "Discard", self)
		player.trike.tab.new_visible(card, "Discard", self)


	# TABLE FUNCTIONS
	# def new_location(self,card,location):
	# self.list[card].clear_quality("location")
	# Lbit = Hanabit("confirmed","location",location,"pos")
	# self.add_bit(Lbit,card)

	# def new_visible(self,card,location):
	# color_bit = Hanabit("confirmed","color",card.color,"final")
	# number_bit = Hanabit("confirmed","number",card.number,"final")
	# self.add_bit(color_bit,card)
	# self.add_bit(number_bit,card)
	# self.new_location(card,location)

	def action(self, ev):
		# Figure out whodunit...
		for p in self.players:
			if p.name == ev.src:
				print("Found the player who is acting.")
				# and make em do it.
				if (ev.type == "Play" or ev.type == "Discard"):
					print("Creating a tempcard.")
					tempcard = Card(ev.id, ev.color, ev.number)
					# Figure out which card in their hand is used
					for card in self.decks[p.name].deck:
						if (card == tempcard):
							print("Found a matching card to play.")
							if ev.type == "Play":
								print("Attempting to play a card.")
								if self.depth == 0:
									print("Attempting to play {}".format(tempcard))
								if self.play_card(card, p):
									ev.bomb = False
								else:
									ev.bomb = True
								if (ev.number == 5 and tempcard in self.play.deck and self.clocks < self.MAX_CLOCKS):
									self.inc_clocks()
								p.draw(self, "game_deck")

							elif ev.type == "Discard":
								self.discard_card(card, p)
								if self.clocks < self.MAX_CLOCKS:
									self.inc_clocks()
								p.draw(self, "game_deck")
				elif ev.type == "Clue":
					self.dec_clocks()
					if self.depth == 0:
						print(ev)
						print("\nThey're in positions:")
					for card in self.decks[ev.tgt].deck:
						# Every card currently in target hand is
						# touched by the clue because negative
						# information counts too
						ev.touch.append(deepcopy(card))
						if ev.color:
							if (card.color == ev.color or card.color == "H"):
								# cards are printed to players in reverse order
								if self.depth == 0:
									print(" {}".format(
										len(self.decks[ev.tgt].deck) - self.decks[ev.tgt].deck.index(card)))
						elif ev.number:
							if (card.number == ev.number):
								# cards are printed to players in reverse order
								if self.depth == 0:
									print(" {}".format(
										len(self.decks[ev.tgt].deck) - self.decks[ev.tgt].deck.index(card)))
			elif p.name == ev.tgt:
				p.trike.bot.receive_clue(ev, p.trike.tab)
				p.trike.con.interpret_clue(ev, p.trike.tab, self)
		#Append the event to my own event log.
		self.past_log.append(ev)
		if self.depth != self.total_depth:
			self.nextgame.action(ev)

	def add_player(self, dude):
		self.players.append(dude)

	def initial_player_order(self, player_name_list):
		npc_names = ["Platypus Bob", "Echidna Jane", "Wallaby Jim", "Ted Imposter", "Matthew Imposter"]
		npc_name_list = []
		if self.variant.playernum < len(player_name_list) + len(npc_name_list):
			print("Too many players for this variant.")
		while (self.variant.playernum > len(player_name_list) + len(npc_name_list)):
			npc_name_list.append(npc_names.pop())
		player_list = []
		for name in player_name_list:
			player_list.append(Player(name, self))
		for name in npc_name_list:
			player_list.append(HanabiNPC(name, self))
		for i in range(len(player_list) - 1):
			player_string = "Who's going "
			if (i == 0):
				player_string += "first?     "
			elif (i == 1):
				player_string += "second?    "
			elif (i == 2):
				player_string += "third?     "
			elif (i == 3):
				player_string += "fourth?    "
			for k, dude in enumerate(player_list):
				player_string += "{} = {}  ".format(k, dude.name)
			next_player = int(input(player_string))
			self.add_player(player_list.pop(next_player))
		self.add_player(player_list.pop())  # the last player is determined by process of elimination
		self.players_initial = deepcopy(self.players)
		self.bot.set_players(self.players_initial)
		for dude in self.players:
			dude.initialize_trike(self)
			self.decks[dude.name].print_distr()

	def initial_hands(self):
		for i in range(self.variant.handsize):
			for dude in self.players:
				dude.draw(self, "game_deck")

	def new_first_player(self):
		self.players.append(self.players.popleft())

	def update_all_tables(self):
		for dude in self.players:
			dude.trike.update_table(self)

	def write_state(self, player):
		ws = open(player.fref, "w")
		ws.truncate()
		ws.write("Clocks: {}".format(self.clocks))
		ws.write("Bombs: {}".format(self.bombs))

		ws.write("Cards in deck (incl. blanks): {}".format(len(self.decks["game_deck"])))
		if self.final_countdown > 0:
			ws.write("Final countdown: {}".format(len(self.players) - self.final_countdown))
		ws.write("\n")

		for dude in self.players_initial:
			if dude.name == player.name:
				if self.players[0].name == player.name:
					ws.write("***You***\n\n")
				else:
					ws.write("You\n\n")
			else:
				if self.players[0].name == dude.name:
					ws.write("***\n" + str(dude) + "'s hand: \n" + str(self.decks[dude.name]) + "***\n\n")
				else:
					ws.write(str(dude) + "'s hand: \n" + str(self.decks[dude.name]) + "\n")
		ws.write(str(self.play))
		ws.write(str(self.discard))

	def write_all_states(self):
		if self.depth == 0:
			print("Clocks: {}".format(self.clocks))
			print("Bombs: {}".format(self.bombs))
			print("Cards in deck (incl. blanks): {}".format(len(self.decks["game_deck"])))
			if self.final_countdown > 0:
				print("Final countdown: {}".format(len(self.players) - self.final_countdown))
			print("\n")
			print(self.play)
			print(self.discard)
		for dude in self.players:
			self.write_state(dude)