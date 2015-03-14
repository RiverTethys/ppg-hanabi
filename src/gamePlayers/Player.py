__author__ = 'Matthew'



class Player(object):
	def __init__(self, name, game):
		self.name = name
		x = HanabiHand(name, game.variant, game.variant.handtemplate)
		game.add_deck(x)
		self.fref = ".\\{}.hanabidata".format(name)
		self.depth = 0
		self.trike = []
		self.nextplayer = []

	def __repr__(self):
		return self.name

	def initialize_trike(self, game):
		self.trike = Tricorder(game, self)

	def draw(self, game, deck):
		card = game.draw_card(deck)
		if card:
			game.decks[self.name].deck.append(card)
			# update tables
			for dude in game.players:
				if dude.name == self.name:
					dude.trike.tab.new_location(card, self.name, game)
				else:
					dude.trike.tab.new_visible(card, self.name, game)

	def set_nextplayer(self, nextplayer):
		self.nextplayer = nextplayer

	def tst_decision(self, game, tstq):
		# dont ask for input because the
		# test has filled in a test action queue
		# TODO: implement cluing for test action queue
		qdec = tstq.pop(0)
		action = qdec[0]
		position = qdec[1]
		target = qdec[2]
		color = qdec[3]
		number = qdec[4]
		current_event = game.future_log.popleft()
		if (action == 'a' or action == 'A'):
			a = game.decks[self.name].deck[-position]
			current_event.make_play(self.name, position, a.id, a.color, a.number)
		elif (action == 'd' or action == 'D'):
			d = game.decks[self.name].deck[-position]
			current_event.make_discard(self.name, position, d.id, d.color, d.number)
		elif (action == 'c' or action == 'C'):
			if color and color != "x":
				current_event.make_clue(self.name
										, game.players_initial[target].name
										, color.upper()
										, None)
			elif number and number != 0:
				current_event.make_clue(self.name
										, game.players_initial[target].name
										, None
										, number)
			else:
				print("Bad clue given in script!")
		return current_event

	def decision(self, game):
		current_event = game.future_log.popleft()
		while (True):
			print("Which action happens this turn? ")
			if (game.clocks > 0):
				action = input("Clue = c / plAy = a / Discard = d\n")
			else:
				action = input("plAy = a / Discard = d\n")

			if (action == 'c' or action == 'C'):
				if (game.clocks < 1):
					print("     ***You don't have any clocks left!***\n")
				else:
					# build clue target options
					if (len(game.players) > 2):
						i = 1
						print("Who do you want to clue?\n")
						for dude in game.players:
							if (dude.name != self.name):
								print("{}. {}\n".format(i, dude.name))
								i += 1
						selection = int(input(" "))
						tgt = game.players[selection]
					else:
						tgt = game.players[1]

					# build clue content options
					print("\nWhat clue do you want to give?")
					# add H back in when we tackle rainbow
					possible_colors = set(game.colors) - set("H")
					possible_numbers = set(game.numbers)

					while True:
						try:
							clue_choice = input("\n")
							if clue_choice.upper() in possible_colors:
								current_event.make_clue(self.name, tgt.name, clue_choice.upper(), None)
								break
							elif int(clue_choice) in possible_numbers:
								current_event.make_clue(self.name, tgt.name, None, int(clue_choice))
								break
							else:
								print("That's not a valid clue choice.\n")
						except AttributeError:
							print("That's not a valid clue choice.\n")
						except ValueError:
							print("That's not a valid clue choice.\n")
					break

			elif (action == 'a' or action == 'A'):
				pos = int(input("Which card? 1=newest,{}=oldest\n".format(game.variant.handsize)))
				a = game.decks[self.name].deck[-pos]
				current_event.make_play(self.name, pos, a.id, a.color, a.number)
				break

			elif (action == 'd' or action == 'D'):
				pos = int(input("Which card? 1=newest,{}=oldest\n".format(game.variant.handsize)))
				d = game.decks[self.name].deck[-pos]
				current_event.make_discard(self.name, pos, d.id, d.color, d.number)
				break
		return current_event

