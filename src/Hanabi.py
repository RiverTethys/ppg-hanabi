#####    RECENT CHANGES    #####
# number of tags suggests importance of the comment 

### A lot of the print statements in HanabiGame now have "if self.depth == 0:"  in front of them to clean up output. May move things around and do this with the deck initializations as well.
### Okay, I have removed the automatic print_distr from Deck initialization. Now only if self.depth == 0 will the game call the deck's print_distr.


##### NEXT ROUND OF TO DO OPTIONS
## q. play conventions and play safety deductions
## w. discard conventions and discard safety deductions
## e. decision flows (this is essentially the main flow, calling all of the other flows based on the conditions of the game.  Most importantly, this is where the list of actions gets initially pared down)
## r. coding and implementing update_table operations
## t. evaluation flows (before, during, and after simulations... at the moment, just before simulations)
## y. determine the extent to which hand-order needs to be considered in tables, etc.
## u. cluing conventions and cluing safety deductions (includes clue interpretations and clue formulation)



#####    TO DO LIST    #####
#suggestion: add even to do things up here, and then migrate them down once the other person has seen them

# we should check if it's okay to dump the Sim files



### progress_a  now has a bool function sims_consistent used to print confirmation that the sims are updating nicely so we only have to print the main game's info.
### You might think about whether we need to check any more details for consistency.

## THIS IS TERRIBLE, but I would like to maybe restructure two things in a big way: give bit-folder .id tags, and find them that way instead of storing them as values to a card key.
## The other thing would be similar, but possibly much lower priority: stop storing decks by name and also just store them in a list,  and maybe write a few functions to get rid of all this .decks[deck_name].deck nonsense.

### Written send_clue in HanabiGame and receive_clue in DeductionBot

#probably convenient to have a "possible values" function in bit...Folder, I think, that eliminates the already-confirmed-negative values from a list of values (for a given quality)
#.... that way we won't see the "you already tried to say that this thing had negative spin" message a bajillion times.

###### Note that bool_query in Table is basically becoming a one-step-from make_bit_pile.  It might be more powerful to simplify it by feeding bool_query lists instead of individual variables.  
######Then we could also implement things like  bool_query_or, bool_query_and  and bool_query_xor .   Also, the new definition of __eq__ for bits might also make these functions simpler

#Moved Event Log into the Game, also had to move initial player order into game and include drawing starting hands in initial player order

#Do you think the None, None might maybe come from the None,None,None,None that you put into the initial future_log?  My guess would be that they aren't being erased by the make_clue etc. functions

#I'm going to lazily NOT make this change because I don't want to mess up your code, but when you're printing hands in reverse (as in action()), you can just use negative indices to save a little space.
#You might even be able to create indices by doing a loop with enumerate instead of .index(), but that's probs just personal preference

#A. Functioning AI
#1. Make-lists function for the table (CHECK?)
#2. Edit color and number deductions (CHECK?)
#3. Convention flows for play
#4. Convention flows for discard
#5. Flows for cluing
#6. Main Flow

#B. Implementation
#1. Initialization (sim games) (CHECK?)
#1.b. having some number of NPCs as well as players (CHECK?)
#2. Feeding info from game to Sim (probably just an Event) (We have the action() part of this, we just need update_table part of this)
#2.a. build an association between a real player and the corresponding sim players (CHECK?)
#3. Make this happen erry turn (information goes in and all of the proper updates happen in the sim, and all of the updates in the sim) (again, done except maybe the AI parts)
#3.b. AI turn vs. Person Turn (this probably happens as we work on the rest of A)

#need input validation on "which card to play/discard" and "who's going first"

#Not 100% sure if Events are going to be used for AI planning, but if they are, we may need some way to track 'intent' (e.g. protective clues, versus playing clues). Right now I'm attempting to use them (that is, the list of possible actions is actually a list of events)

from HanabiClasses import *


def sims_consistent(games):
	for x in games:
		for y in games[0].decks:
			if x.decks[y].deck != games[0].decks[y].deck:
				return False
		for a,b in zip(x.players,games[0].players):
			if a.name != b.name:
				return False
		if x.clocks != games[0].clocks or x.bombs != games[0].bombs:
			return False
	return True

def update_tables(games):
	for x in games:
		for p in x.players:
			p.trike.update_table(x)

def print_table_location_list(games,game_name,player_name,location_name):
	for x in games:
		if game_name == x.name:
			for p in x.players:
				if player_name == p.name:
					AAA = p.trike.tab.get_location_list(location_name)
					for aaa in AAA:
						if len(AAA[aaa].pile) >0:
							print ( str(aaa)+": "+str(AAA[aaa]))
					print("\n")
						
def print_locations(games):
	update_tables(games)
	for x in games:
		print("\n\n**********"+x.name + "**********:\n")
		for p in x.players:
			print("\n---"+p.name+"---:\n")
			for l in x.decks:
				print(l+":\n")
				print_table_location_list(games,x.name,p.name,l)
		print("\n")
				
					
def print_table_list(games,game_name,player_name,type,quality,value,spin):
	for x in games:
		if game_name == x.name:
			for p in x.players:
				if player_name == p.name:
					print (p.trike.tab.make_short_list(type,quality,value,spin))

def turn(games):
	active_player = games[0].players[0]
	print("{}'s turn:\n".format(active_player.name))
	dec = active_player.decision(games[0])
	for each_game in games:
		each_game.action(dec)
	
	if (len(games[0].decks["game_deck"]) == 0):
		games[0].inc_fc()
	if (games[0].final_countdown > len(games[0].players)):
		games[0].victory = True
	for x in games:	
		x.new_first_player()
	if sims_consistent(games):
		consistent = "\nThe sim games are consistent with the real game.\n"
	else:
		consistent = "\nUh oh.\nThe sim games are NOT consistent with the real game.\n"
	print(consistent)
	# Update sim games with new change in the real game					

def write_data(games):
	for x in games:	
			x.write_all_states()
	
def initialize_hanabi():  ##Separated so that we can test things more easily on the command line
	#CARD_COLORS = ['R','Y','G','B','W','H']
	CARD_COLORS = ['R','Y','G','B','W']
	CARD_NUMBERS = [1,2,3,4,5]
	#deck_template = HanabiDeckTemplate(CARD_COLORS,CARD_NUMBERS,{x:{1:3,2:2,3:2,4:2,5:1} for x in ('R','Y','G','B','W','H')})
	deck_template = HanabiDeckTemplate(CARD_COLORS,CARD_NUMBERS,{x:{1:3,2:2,3:2,4:2,5:1} for x in ('R','Y','G','B','W')})
	
	variant = HanabiVariant(2,5,deck_template,[])

	bot = DeductionBot(variant)
	
	player_name_list = ["Ted","Matthew"]
	
	SIM_DEPTH = 2
	game = HanabiGame("The Overworld",variant,[],bot,player_name_list,SIM_DEPTH,0)
	
	sim_name_list= []
	for dude in game.players_initial:
		sim_name_list.append(dude.name)
	games = [game]
	for i in range(SIM_DEPTH):
		games.append(HanabiSim("sim" + str(i+1), game, sim_name_list, i + 1))
	
	
	#for testing...
	print("[Game, player list, deck size]:")
	for x in games:
		print(str([x,[y for y in x.players], len(x.decks["game_deck"] )]))
	
	
	starting_deck = deepcopy(games[0].decks["game_deck"].deck)
	i=0
	for card in starting_deck:
		print("{}. {}".format(i,card))
		i += 1
	
	games[0].write_all_states()
	if sims_consistent(games):
		consistent = "\nThe sim games are consistent with the real game.\n"
	else:
		consistent = "\nUh oh.\nThe sim games are NOT consistent with the real game.\n"
	print(consistent)
	return games
	
def play_hanabi():
		
	games = initialize_hanabi()
	game = games[0]
	
	while(not (game.defeat or game.victory)):
		
		turn(games)
		write_data(games)
		
	
	if game.defeat:
		print("YOU'VE FAILED!")
	elif game.victory:
		print("You have completed the firework show with a score of {}.".format(len(game.play)))
	else:
		print("Whoa whoa WHOA. You should NOT be seeing this!")
		
	for elt in game.past_log:
		print(elt)

if __name__ == "__main__":		
	play_hanabi()








