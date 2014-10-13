from game_classes import *
from hanabi_classes import *

def play_hanabi():
	CARD_COLORS = ['R','Y','G','B','W','H']
	CARD_NUMBERS = [1,2,3,4,5]
	deck_template = HanabiDeckTemplate(CARD_COLORS,CARD_NUMBERS,{x:{1:3,2:2,3:2,4:2,5:1} for x in ('R','Y','G','B','W','H')})
	
	variant = HanabiVariant(2,5,deck_template,[])

	game = HanabiGame("testing",variant,[])
	
	player1 = Player("Player 1",game)
	player2 = Player("Player 2",game)
	player_list = [player1,player2]
	
	game.initial_player_order(player_list)
	
	# for testing...
	i=0
	for card in game.decks["game_deck"].deck:
		print("{}. {}".format(i,card))
		i += 1

	for i in range(game.variant.handsize):
		for dude in game.players:
			dude.draw(game,"game_deck")
	
	print("Cards in deck: {}".format(len(game.decks["game_deck"])))
	
	#calculate maximum length of log
	NUM_PLAYS_TO_WIN = len(CARD_COLORS) * len(CARD_NUMBERS)
	NUM_OF_FIVES = len(CARD_COLORS)
	INITIAL_CLOCKS = variant.clocks
	INITIAL_DECK_SIZE = len(game.decks["game_deck"])
	NUM_PLAYERS = len(game.players)
	MAX_TURNS = NUM_PLAYS_TO_WIN + INITIAL_CLOCKS + NUM_OF_FIVES + 2*(INITIAL_DECK_SIZE - NUM_PLAYS_TO_WIN) - 1 + NUM_PLAYERS
	
	#initialize Future Log
	future_log = deque([HanabiEvent(None,None,None,None,None) for x in range(MAX_TURNS)])
	past_log = []
	# for testing...
	starting_deck = deepcopy(game.decks["game_deck"].deck)
	i=0
	for card in starting_deck:
		print("{}. {}".format(i,card))
		i += 1
	
	
	
	game.write_all_states()

	while(not (game.defeat or game.victory)):
		print("{}'s turn:\n".format(game.players[0].name))
		turn(game,"game_deck",future_log,past_log)
		if (len(game.decks["game_deck"]) == 0):
			game.inc_fc()
		if (game.final_countdown > len(game.players)):
			game.victory = True
		game.write_all_states()
		game.new_first_player()
		
	if game.defeat:
		print("YOU'VE FAILED!")
	elif game.victory:
		print("You have completed the firework show with a score of {}.".format(len(game.play)))
	else:
		print("Whoa whoa WHOA. You should NOT be seeing this!")
		
	for elt in past_log:
		print(elt)
		
play_hanabi()