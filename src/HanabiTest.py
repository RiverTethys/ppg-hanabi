from Hanabi import *

def tst_init_hanabi(test_number):  ##Currently doesnt deal with sims
	CARD_COLORS = ['R','Y','G','B','W']
	CARD_NUMBERS = [1,2,3,4,5]
	deck_template = HanabiDeckTemplate(CARD_COLORS,CARD_NUMBERS,{x:{1:3,2:2,3:2,4:2,5:1} for x in ('R','Y','G','B','W')})
	variant = HanabiVariant(3,5,deck_template,[])
	bot = DeductionBot(variant)
	SIM_DEPTH = 0
	game = HanabiGame("Test world {}".format(test_number),variant,[],bot,SIM_DEPTH,0)
	game.set_game_deck(deckfile=".\\testdeck{}.hanabideck".format(test_number))
	game.set_stacks()
	player_name_list = ["Ted","Matthew"]
	game.initial_player_order(player_name_list)
	game.update_all_tables()
	game.initial_hands()
	game.set_game_log()
	game.set_conventions(HanabiConventions(game))
	
	for enum, card in enumerate(game.decks["game_deck"].deck):
		print("{}. {}".format(enum,card))
	
	game.write_all_states()

	return [game]
	
def tst_turn(games,tstq):
	active_player = games[0].players[0]
	print("{}'s turn:\n".format(active_player.name))
	dec = active_player.tst_decision(games[0],tstq)
	for each_game in games:
		print(dec)
		print(dec.id)
		each_game.action(dec)
	
	if (len(games[0].decks["game_deck"]) == 0):
		games[0].inc_fc()
	if (games[0].final_countdown > len(games[0].players)):
		games[0].victory = True
	for x in games:	
		x.new_first_player()
		
	# if sims_consistent(games):
		# consistent = "\nThe sim games are consistent with the real game.\n"
	# else:
		# consistent = "\nUh oh.\nThe sim games are NOT consistent with the real game.\n"
	# print(consistent)
	# Update sim games with new change in the real game					
	
def tst_play_hanabi(test_number):
		
	games = tst_init_hanabi(test_number)
	game = games[0]
	
	# Create the test queue of actions...
	tstq = []
	with open(".\\testscript{}.hanabiscript".format(test_number)) as fileref:
		for entry in fileref:
			m = re.search('^([acd])([12345])$',entry)
			tstq.append([m.group(1),int(m.group(2))])
	
	while(tstq and not (game.defeat or game.victory)):
		
		tst_turn(games,tstq)
		write_data(games)
		
	
	if game.defeat:
		print("YOU'VE FAILED!")
	elif game.victory:
		print("You have completed the firework show with a score of {}.".format(len(game.play)))
	else:
		print("Whoa whoa WHOA. You should NOT be seeing this!")
		
	for elt in game.past_log:
		print(elt)









