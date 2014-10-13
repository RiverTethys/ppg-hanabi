#need input validation on "which card to play/discard" and "who's going first"
#the card list should not be part of game.decks b/c it duplicates the card IDs. Should be a separate attr

#Even human players will need an AIBot built into them, so that AI's can use them.  Thus, the NPCs and PCs will be the same except for how they take their own turns.
#Going to have to make player.playable in addition to game.playable in order for players to check to see if a card in their own hand is playable (probably checking the Hanabits)
#Speaking of Hanabits, if we implement this structure, we'll basically need to be able to tag anything with them, so maybe initialize everything with an empty bits list.
#Not 100% sure if Events are going to be used for AI planning, but if they are, we may need some way to track 'intent' (e.g. protective clues, versus playing clues). Right now I'm attempting to use them (that is, the list of possible actions is actually a list of events)
#Hadn't thought of it quite this way before... there's a good chance that when the AI is going, it may be convenient to edit knowledge mid-flow.  If we end up doing this, then instead of using other players' AI bots to run simulations it may be better to clone an imperfect mini-game based on personal knowledge and have the cloned players run the simulation. (or we could always add a toggle that disallows saving knowledge)

#right now there's nothing to enforce each card being in only one place at a time.
#Zone???
#The relationship between Variant and Game need to be worked out



from copy import deepcopy
from collections import deque
from game_classes import *

class HanabiGameDeck(Deck):
	def __init__(self,name,vnt):
		Deck.__init__(self,name,vnt)
		self.name = name
		self.distr = vnt.decktemplate.distr
		self.deck = self.build_deck()
		
class HanabiHand(Deck):
	def __init__(self,name,vnt):
		Deck.__init__(self,name,vnt)
		self.name = name
		self.distr = vnt.handtemplate.distr
		self.deck = self.build_deck()
		
class HanabiStacks(Deck):
	def __init__(self,name,vnt):
		Deck.__init__(self,name,vnt)
		self.name = name
		self.distr = vnt.stackstemplate.distr
		self.deck = self.build_deck()
		
		
	def __repr__(self):
		
		x = {a:[] for a in self.colors}
		for card in self.deck:
			x[card.color].append(card)
			
		y = ""
		y+= "\n{} Stacks:\n".format(self.name)
		for i in x:
			y+=str(x[i])
			y+="   "
		
		return y

class Player(object):
	def __init__(self,name,game):
		self.name = name
		self.hand = HanabiHand(name,game.variant)
		self.c = self.hand.deck
		self.knowledge = {}
		self.fref = ".\\{}.hanabidata".format(name)
	
	def __repr__(self):
		x = "{}'s hand: \n   1 ---> {}\n".format(self.name,len(self.c))
		for card in reversed(self.c):
			x+=str(card)
		x+="\n"
		return x
	def draw(self,game,deck):
		self.c.append(game.draw(deck))
	def discard(self,game,pos,deck):
		d = self.c[-pos]
		color = self.c[-pos].color
		game.discard_card(self.c.pop(-pos))
		self.draw(game,deck)
		return d
	def play(self,game,pos,deck):
		a=self.c[-pos]	
		color = a.color
		game.play_card(self.c.pop(-pos))
		self.draw(game,deck)
		return a
	def clue(self,player,clue):
		pass
	
class HanabiGame(object):
	def __init__(self,name,variant,conventions):
		self.name = name
		self.variant = variant
		self.colors = variant.colors
		self.values = variant.values
		self.distr = variant.decktemplate.distr
		self.players = deque([])
		self.players_initial=[]
		self.rules = variant.rules
		self.play = []
		self.discard = []
		self.clocks = variant.clocks
		self.MAX_CLOCKS = variant.clocks
		self.bombs = variant.bombs
		self.MAX_BOMBS = variant.bombs
		self.fref = ".\\{}.hanabilog".format(name)
		self.con = conventions		
		self.defeat = False
		self.victory = False
		self.final_countdown = 0
		
		self.decks = {}
		self.set_game_deck()
		self.set_stacks()
		
	def set_game_deck(self):
		self.add_deck(HanabiGameDeck("card_list",self.variant))
		game_deck = HanabiGameDeck("game_deck",self.variant)
		game_deck.shuffle()
		self.add_deck(game_deck)
		
	def set_stacks(self):
		self.add_deck(HanabiStacks("Play",self.variant))
		self.add_deck(HanabiStacks("Discard",self.variant))
		self.play = self.decks["Play"]
		self.discard = self.decks["Discard"]
		
	def add_deck(self,deck):
		self.decks[deck.name] = deck
	
	def inc_clocks(self):
		self.clocks += 1
		
	def dec_clocks(self):
		self.clocks -= 1
		
	def inc_fc(self):
		self.final_countdown += 1
		
	def draw_card(self,deckname):
		return self.decks[deckname].draw()
	
	def playable(self,card):
		for x in self.play.deck:
			if (x.color == card.color and x.num == card.num):
				return False
		if card.num == 1:
			return True
		for x in self.play.deck:
			if (x.color == card.color and x.num == (card.num - 1) ):
				return True
		return False
	
	def play_card(self,card):
		if self.playable(card):
			self.play.add(card)
			if len(self.play) == 30: #need to change this to reference a value based on the variant
				self.victory = True
		else:
			self.bomb()
			self.discard_card(card)	
		
	def discard_card(self,card):
		self.discard.add(card)
		
	def draw(self,deck):
		return self.decks[deck].draw()

	def bomb(self):
		self.bombs-=1
		if (self.bombs==0):
			self.defeat = True
	
	def add_player(self,dude):
		self.players.append(dude)
	
	def initial_player_order(self,player_list):
	
		for i in range(len(player_list)-1):
			player_string = "Who's going "
			if(i==0):
				player_string+="first?     "
			elif(i==1):
				player_string+="second?    "
			elif(i==2):
				player_string+="third?     "
			elif(i==3):
				player_string+="fourth?    "	
			for k,dude in enumerate(player_list):
				player_string+="{} = {}  ".format(k,dude.name)
			next_player = int(input(player_string))
			self.add_player(player_list.pop(next_player))
		self.add_player(player_list.pop()) #the last player is determined by process of elimination
		self.players_initial = self.players
		
	def new_first_player(self):
		self.players.append(self.players.popleft())
	
	def write_state(self,player):
		ws = open(player.fref,"w")
		ws.truncate()
		ws.write("Clocks: {}\n".format(self.clocks))
		
		ws.write("Bombs: {}\n".format(self.bombs))
		
		ws.write("Cards in deck: {}\n\n".format(len(self.decks["game_deck"])))
		
		for dude in self.players_initial:
			if dude.name == player.name:
				if self.players[0].name == player.name:
					ws.write("***You***\n\n")
				else:
					ws.write("You\n\n")
			else:
				if self.players[0].name == dude.name:
					ws.write("***\n"+str(dude)+"***\n\n")
				else:
					ws.write(str(dude)+"\n")
		ws.write(str(self.play))
		ws.write(str(self.discard))
	
	def write_all_states(self):
		print("Clocks: {}\n".format(self.clocks))
		print("Bombs: {}\n".format(self.bombs))		
		print("Cards in deck: {}\n\n".format(len(self.decks["game_deck"])))
		print(self.play)
		print(self.discard)
		for dude in self.players:
			self.write_state(dude)
	
	def clone(self):
		x = deepcopy(self)
		return x

def turn(game,deck,upcoming,past):
	active_player = game.players[0]
	current_event = upcoming.popleft()
	while(True):
		print("Which action happens this turn? ")
		if (game.clocks > 0):
			action = input("Clue = c / plAy = a / Discard = d\n")
		else:
			action = input("plAy = a / Discard = d\n")
		if (action=='c' or action=='C'):
			if (game.clocks < 1):
				print("     ***You don't have any clocks left!***\n")
			else:
				#build clue target options
				if (len(game.players) > 2):
					i = 1
					print ("Who do you want to clue?\n")
					for dude in game.players:
						if (dude.name != active_player.name):
							print ("{}. {}\n".format(i,dude.name))
							i += 1
					selection = int(input(" "))
					tgt = game.players[selection]
				else:
					tgt = game.players[1]
					
				#build clue content options
				print("\nWhat clue do you want to give?")
				possible_colors = set()
				possible_numbers = set()
				for card in tgt.hand.deck:
					if (card.color != "H"):
						possible_colors.add(card.color)
					possible_numbers.add(card.num)
				print("\nColors: ")
				for color in possible_colors:
					print("{} ".format(color))
				print("\nNumbers: ")
				for number in possible_numbers:
					print("{} ".format(number))

				while True:
					try:
						clue_choice = input("\n")
						if clue_choice.upper() in possible_colors:
							current_event.make_clue(active_player,tgt,None,clue_choice.upper())
							print(current_event)
							print("\nThey're in positions:")
							for card in tgt.hand.deck:
								if (card.color == clue_choice.upper() or card.color == "H"):
									# cards are printed to players in reverse order
									print(" {}".format(len(tgt.hand.deck) - tgt.hand.deck.index(card)))
							break
						elif int(clue_choice) in possible_numbers:
							current_event.make_clue(active_player,tgt,clue_choice,None)
							print(current_event)
							print("\nThey're in positions:")
							for card in tgt.hand.deck:
								if (card.num == int(clue_choice)):
									# cards are printed to players in reverse order
									print(" {}".format(len(tgt.hand.deck) - tgt.hand.deck.index(card)))
							break
						else:
							print("That's not a valid clue choice.\n")
					except AttributeError:
						print("That's not a valid clue choice.\n")
					except ValueError:
						print("That's not a valid clue choice.\n")
					
				game.dec_clocks()
				break
				
		elif (action=='a'or action=='A'):
			a = active_player.play(game,int(input("Which card? 1=newest,{}=oldest\n".format(game.variant.handsize))),deck)
			if(a.num==5 and a in game.play.deck and game.clocks < game.MAX_CLOCKS):
				game.inc_clocks()
			current_event.make_play(active_player,a.num,a.color)
			break
			
		elif (action=='d' or action=='D'):
			d = active_player.discard(game,int(input("Which card? 1=newest,{}=oldest\n".format(game.variant.handsize))),deck)
			if (game.clocks < game.MAX_CLOCKS):
				game.inc_clocks()
			current_event.make_discard(active_player,d.num,d.color)
			break
			
	past.append(current_event)

class HanabiDeckTemplate(object):
	def __init__(self,colors,values,distr):
		self.colors = colors
		self.values = values
		self.distr = distr

	def __len__(self):
		size = 0
		for color in self.colors:
			for num in self.distr[color]:
				size+=num
		return size

class HanabiVariant(object):
	def __init__(self,playernum,handsize,decktemplate,rules):
		self.playernum = playernum
		self.handsize = handsize
		self.clocks = 8
		self.bombs = 3
		self.colors = decktemplate.colors
		self.values = decktemplate.values
		self.decktemplate = decktemplate
		self.handtemplate = HanabiDeckTemplate(decktemplate.colors,decktemplate.values,{x:{y:0 for y in decktemplate.values} for x in decktemplate.colors})
		self.stackstemplate = HanabiDeckTemplate(decktemplate.colors,decktemplate.values,{x:{y:0 for y in decktemplate.values} for x in decktemplate.colors})
		self.rules = rules


class HanabiEvent(object):
	def __init__(self,src,tgt,type,number,color):
		self.src = src
		self.tgt = tgt
		self.type = type # "Play", "Discard", or "Clue"
		self.number = number
		self.color = color
		
	def __repr__(self):
		if (self.src == None):
			repstr = "Null Hanabi event"
		else:
			repstr = "{} decided to {} ".format(self.src.name,self.type)
			if (type == "Clue"):
				repstr += "{}".format(self.tgt.name)
				if (self.number != None):
					repstr += " about {}'s.".format(self.number)
				elif (self.color != None):
					repstr += " about {}'s.".format(self.color)
				else:
					repstr += "... about what, we may never know."
			else:
				repstr += "{}{}.".format(self.number,self.color)
		return repstr
	
	def make_clue(self,src,tgt,number,color):
		self.src = src
		self.tgt = tgt
		self.type = "Clue"
		self.number = number
		self.color = color
		
	def make_play(self,src,number,color):
		self.src = src
		self.type = "Play"
		self.number = number
		self.color = color
		
	def make_discard(self,src,number,color):
		self.src = src
		self.type = "Discard"
		self.number = number
		self.color = color





