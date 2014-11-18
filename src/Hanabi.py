#####    RECENT CHANGES    #####
# number of tags suggests importance of the comment 

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

## In progress_a, more calls are looped over all of the games (so that it works right)

### A lot of the print statements in HanabiGame now have "if self.depth == 0:"  in front of them to clean up output. May move things around and do this with the deck initializations as well.

### progress_a  now has a bool function sims_consistent used to print confirmation that the sims are updating nicely so we only have to print the main game's info.
### You might think about whether we need to check any more details for consistency.

## THIS IS TERRIBLE, but I would like to maybe restructure two things in a big way: give bit-folder .id tags, and find them that way instead of storing them as values to a card key.
## The other thing would be similar, but possibly much lower priority: stop storing decks by name and also just store them in a list,  and maybe write a few functions to get rid of all this .decks[deck_name].deck nonsense.

#probably convenient to have a "possible values" function in bit...Folder, I think, that eliminates the already-confirmed-negative values from a list of values (for a given quality)
#.... that way we won't see the "you already tried to say that this thing had negative spin" message a bajillion times.

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

#Not 100% sure if Events are going to be used for AI planning, but if they are, we may need some way to track 'intent' (e.g. protective clues, versus playing clues). Right now I'm attempting to use them (that is, the list of possible actions is actually a list of events)

from HanabiConventionFlows import *
from HanabiDeductionFlows import *
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
					location_dict = p.trike.tab.location[location_name]
					for card in location_dict:
						if len(location_dict[card].pile) >0:
							print ( str(card)+": "+str(location_dict[card]))
					print("\n")
						
def print_locations(games):
	update_tables(games)
	for x in games:
		print("\n\n**********"+x.name + "**********:\n")
		for p in x.players:
			print("\n---"+p.name+"---:\n")
			print("Play Queue: "+str(p.trike.tab.play_q)+"\nDiscard Queue: "+str(p.trike.tab.discard_q)+"\n")
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
	for each_game in games:
		each_game.update_all_tables()
	active_player = games[0].players[0]
	print("{}'s turn:\n".format(active_player.name))
	dec = active_player.decision(games[0])
	for each_game in games:
		print(dec)
		print(dec.id)
		each_game.action(dec)
	
	if (len(games[0].decks["game_deck"]) == 0 ):
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
	distr = {x:{1:3,2:2,3:2,4:2,5:1} for x in ('R','Y','G','B','W')}
	deck_template = HanabiDeckTemplate(CARD_COLORS,CARD_NUMBERS,distr)
	
	##(playernum,handsize,deck_template,[])
	variant = HanabiVariant(4,4,deck_template,[])

	bot = DeductionBot(variant)
	player_name_list = []
	SIM_DEPTH = 0
	game = HanabiGame("The Overworld",variant,[],bot,SIM_DEPTH,0)
	game.set_game_deck()
	game.set_stacks()
	game.initial_player_order(player_name_list)
	game.update_all_tables()
	game.initial_hands()
	game.set_game_log()
		
	sim_name_list= []
	for dude in game.players_initial:
		sim_name_list.append(dude.name)
	games = [game]
	for i in range(SIM_DEPTH):
		games.append(HanabiSim("sim" + str(i+1), game, i + 1))
		games[i+1].set_game_deck()
		games[i+1].set_stacks()
		games[i+1].initial_player_order(sim_name_list)
		games[i+1].update_all_tables()
		games[i+1].initial_hands()
		games[i+1].set_game_log()	
		
	for x in games:
		x.set_conventions(HanabiConventions(x))
	
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
		#try:
		turn(games)
		write_data(games)
		#except:
		#	logref = open("HanabiLog.hanabilog","w")
		#	for elt in game.past_log:
		#		logref.write(str(elt)+"\n")
		#	logref.close()
		#	break
	
	if game.defeat:
		print("YOU'VE FAILED!")
	elif game.victory:
		print("\n**************************************************************")
		print("*  You have completed the firework show with a score of {}.  *".format(len(game.play)))
		print("**************************************************************\n")
	else:
		print("Whoa whoa WHOA. You should NOT be seeing this!")
		
	logref = open("HanabiLog.hanabilog","w")
	response = input("\nSave this game's deck? (y/n) ")
	if response.upper() == "Y":
		newscript = open("newscript.hanabiscript","w")
		newdeck = open("newdeck.hanabideck","w")
		for elt in game.past_log:
			print(elt)
			logref.write(str(elt)+"\n")
			#write the event in script format.
			#probably requires that Events track
			#hand position for plays/discards.
		newscript.close()
		for card in game.initial_game_deck.deck:
			newdeck.write("{}".format(card))
		newdeck.close()
		print("Remember to rename the new deck file if you want to keep it.")
	else:
		for elt in game.past_log:
			print(elt)
			logref.write(str(elt)+"\n")
	logref.close()
		
if __name__ == "__main__":		
	play_hanabi()








