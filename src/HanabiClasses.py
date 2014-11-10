from collections import deque
import random
from copy import deepcopy

class Card(object):
	def __init__(self,id,color,number):
		self.id = id
		self.number = number
		self.color = color
	
	def __repr__(self):
		return str(self.number) + self.color + " "

	def __str__(self):	
		return str(self.number) + self.color + " "
		
	def __eq__(self,other):
		return (self.id == other.id and self.color == other.color and self.number == other.number)
	
	def __hash__(self):
		return hash(self.id)

class Deck(object):
	def __init__(self,name,vnt,template):
		self.colors  = vnt.colors
		self.numbers = vnt.numbers
		self.name = name
		self.distr = template.distr
		self.deck = self.build_deck()
		
	def set_distr(self,distr):
		self.distr = distr
	
	def print_distr(self):
		#print("{} distr:  {}".format(self.name,str(self.distr)))
		print("{} distr:".format(self.name))
		r = ""
		for c in self.colors:
			for n, q in self.distr[c].items():
				if not (q == 0):
					r = r + "{}{}: {}  ".format(c,n,q)
			r = r + "\n"
		if not r.replace("\n",""):
			print("Empty.\n")
		else:
			print(r)
		
	def build_deck(self):
		deck = []
		card_id = 0	
		for color in self.distr:
			for num in self.distr[color]:
				for i in range(self.distr[color][num]):
					deck.append(Card(card_id,color,num))
					card_id += 1
		return deck
		
	def shuffle(self):
		random.shuffle(self.deck)

	def draw(self):
		if (len(self.deck) == 0):
			print("Tried to draw from an empty deck.")
			return
		return self.deck.pop()
	
	def add(self,card):
		self.deck.append(card)
	
	def __len__(self):
		return len(self.deck)

class HanabiGameDeck(Deck):
	#def __init__(self,name,vnt,template):
		#Deck.__init__(self,name,vnt,template)
		#self.name = name
		#self.distr = vnt.decktemplate.distr
		#self.deck = self.build_deck()
	def filler():
		print("ooh lookit me, I'm filler")
		
class HanabiHand(Deck):
	#def __init__(self,name,vnt,template):
		#Deck.__init__(self,name,vnt,template)
		#self.name = name
		#self.distr = vnt.handtemplate.distr
		#self.deck = self.build_deck()
		
	def __repr__(self):
		x = "   1 ---> {}\n".format(len(self.deck))
		for card in reversed(self.deck):
			x+=str(card)
		x+="\n"
		return x
	
class HanabiStacks(Deck):
	#def __init__(self,name,vnt,template):
		#Deck.__init__(self,name,vnt)
		#self.name = name
		#self.distr = vnt.stackstemplate.distr
		#self.deck = self.build_deck()
	
		
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

class HanabiDeckTemplate(object):
	def __init__(self,colors,numbers,distr):
		self.colors = colors
		self.numbers = numbers
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
		self.numbers = decktemplate.numbers
		self.decktemplate = decktemplate
		self.handtemplate = HanabiDeckTemplate(decktemplate.colors,decktemplate.numbers,{x:{y:0 for y in decktemplate.numbers} for x in decktemplate.colors})
		self.stackstemplate = HanabiDeckTemplate(decktemplate.colors,decktemplate.numbers,{x:{y:0 for y in decktemplate.numbers} for x in decktemplate.colors})
		self.rules = rules

class Player(object):
	def __init__(self,name,game):
		self.name = name
		x = HanabiHand(name,game.variant,game.variant.handtemplate)
		game.add_deck(x)
		self.fref = ".\\{}.hanabidata".format(name)
		self.depth = 0
		self.trike = []
	
	def __repr__(self):
		return self.name
	
	def initialize_trike(self,game):
		self.trike = Tricorder(game,self)
	
	def draw(self,game,deck):
		card = game.draw_card(deck)
		game.decks[self.name].deck.append(card)
		#update tables
		for dude in game.players:
			dude.trike.tab.new_location(card,self.name,game)
			if dude.name != self.name:
				dude.trike.tab.new_visible(card,self.name,game)
		
	# deprecated. i want it to break if something is still calling these.
	# def discard(self,game,pos,deck):
		# d = game.decks[self.name].deck[-pos]
		# color = game.decks[self.name].deck[-pos].color
		# game.discard_card(game.decks[self.name].deck.pop(-pos))
		# self.draw(game,deck)
		# return d
		
		
	# def play(self,game,pos,deck):
		# a=game.decks[self.name].deck[-pos]	
		# color = a.color
		# game.play_card(game.decks[self.name].deck.pop(-pos))
		# self.draw(game,deck)
		# return a
	
		
	#def clue(self,player,clue):
	#	pass
	
	def decision(self,game):
		current_event = game.future_log.popleft()
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
							if (dude.name != self.name):
								print ("{}. {}\n".format(i,dude.name))
								i += 1
						selection = int(input(" "))
						tgt = game.players[selection]
					else:
						tgt = game.players[1]
						
					#build clue content options
					print("\nWhat clue do you want to give?")
					possible_colors = set(game.colors) - set("H")
					possible_numbers = set(game.numbers)
					# We dont display allowed clues because technically you
					# can clue about having 0 of something
					# print("\nColors: ")
					# for color in possible_colors:
						# print("{} ".format(color))
					# print("\nNumbers: ")
					# for number in possible_numbers:
						# print("{} ".format(number))

						
					# dont need to call game.action because the return value
					# is being used in a call to it at the top level
					while True:
						try:
							clue_choice = input("\n")
							if clue_choice.upper() in possible_colors:
								current_event.make_clue(self.name,tgt.name,clue_choice.upper(),None)
								break
							elif int(clue_choice) in possible_numbers:
								current_event.make_clue(self.name,tgt.name,None,int(clue_choice))
								break
							else:
								print("That's not a valid clue choice.\n")
						except AttributeError:
							print("That's not a valid clue choice.\n")
						except ValueError:
							print("That's not a valid clue choice.\n")
					break
					
			elif (action=='a' or action=='A'):
				a = game.decks[self.name].deck[-int(input("Which card? 1=newest,{}=oldest\n".format(game.variant.handsize)))]
				current_event.make_play(self.name,a.id,a.color,a.number)
				break
				
			elif (action=='d' or action=='D'):
				d = game.decks[self.name].deck[-int(input("Which card? 1=newest,{}=oldest\n".format(game.variant.handsize)))]
				current_event.make_discard(self.name,d.id,d.color,d.number)
				break
		return current_event
		
class HanabiEvent(object):
	def __init__(self,src,tgt,type,id,color,number):
		self.src = src
		self.tgt = tgt
		self.type = type # "Play", "Discard", or "Clue"
		self.id = id
		self.color = color
		self.number = number
		self.touch = []
		
	def __repr__(self):
		if (self.src == None):
			repstr = "Null Hanabi event"
		else:
			repstr = "{} decided to {} ".format(self.src,self.type)
			if (type == "Clue"):
				repstr += "{}".format(self.tgt)
				if (self.number != None):
					repstr += " about {}'s.".format(self.number)
				elif (self.color != None):
					repstr += " about {}'s.".format(self.color)
				else:
					repstr += "... about what, we may never know."
			else:
				repstr += "{}{}.".format(self.number,self.color)
		return repstr
	
	def make_clue(self,src,tgt,color,number):
		self.src = src
		self.tgt = tgt
		self.type = "Clue"
		self.color = color
		self.number = number

	def make_play(self,src,id,color,number):
		self.src = src
		self.type = "Play"
		self.id = id
		self.color = color
		self.number = number

	def make_discard(self,src,id,color,number):
		self.src = src
		self.type = "Discard"
		self.id = id
		self.color = color
		self.number = number

	def __init__(self,type,subtype,game):
		self.type=type
		self.subtype=subtype

def create_all_choices(player,game):
	allc = []
	#Create plays and discards
	p = [Choice(action = "Play",pos = x+1) for x in range(game.variant.handsize)]
	d = [Choice(action = "Discard",pos = x+1) for x in range(game.variant.handsize)]
	#Create clues
	c = []
	for pl in game.players:
		if pl.name != player.name:
			c = c + [Choice(action = "Clue",tgt = pl.name,color = cl) for cl in game.colors]
			c = c + [Choice(action = "Clue",tgt = pl.name,number = nm) for nm in game.numbers]
	allc = p + d + c
	return allc
	
def ikyk(game,player,other):
	temptab = BitTable(game,pl=player)
	temptab.update_location_list(game)
	temptab.update_critical_list(game)
	for card in game.play.deck:
		temptab.add_bit(Hanabit("confirmed","color",card.color,"final",temptab),card)
		temptab.add_bit(Hanabit("confirmed","number",card.number,"final",temptab),card)
	for card in game.discard.deck:
		temptab.add_bit(Hanabit("confirmed","color",card.color,"final",temptab),card)
		temptab.add_bit(Hanabit("confirmed","number",card.number,"final",temptab),card)
	for pl in game.players:
		for card in game.decks[pl.name].deck:
			if (pl.name != player.name and pl.name != other.name):
				temptab.add_bit(Hanabit("confirmed","color",card.color,"final",temptab),card)
				temptab.add_bit(Hanabit("confirmed","number",card.number,"final",temptab),card)
	#Consult the log to find all clues given regarding 
	#cards *currently* not visible to each of the two players.
	#Add only the content of those clues to the temp table
	#This will have to change when rainbow is added back in.
	for ev in game.past_log:
		if (ev.type == "Clue" and (ev.tgt == player.name or ev.tgt == other.name)):
			DeductionBot(game.variant).receive_clue(ev,temptab)
	game.con.order_play_q(temptab)
	game.con.order_discard_q(temptab)
	return temptab

def eval_flow(player,game):
	chs = create_all_choices(player,game)
	clocks_are_low = (game.MAX_CLOCKS/2) - game.clocks
	# go through the hand. score playables, score others as discardable
	for enum, c in enumerate(game.decks[player.name].deck):
		if player.trike.tab.list[c].query_bit_pile(qtype=["confirmed","conventional"] 
											  ,qquality=["playability"]
											  ,qvalue=["playable"]
											  ,qspin=["pos","final"]):
			for i in chs:
				if i.action == "Play" and i.pos == (len(game.decks[player.name].deck) - enum):
					i.bump(10)
		elif player.trike.tab.list[c].query_bit_pile(qtype=["default","conventional"] 
											    ,qquality=["discardability"]
											    ,qvalue=["discardable"]
												,qspin=["default","pos","final"]):
			for i in chs:
				if i.action == "Discard" and i.pos == (len(game.decks[player.name].deck) - enum):
					for num, elt in enumerate(player.trike.tab.discard_q):
						if elt == c:
							qpos = num
					i.bump(1 + len(player.trike.tab.discard_q) - qpos) 
	# evaluate clues based on type of clue theyll think it is
	for i in chs:
		if i.action == "Clue":
			pred = game.con.predict_clue(HanabiEvent(player,i.tgt,"Clue",None,i.color,i.number)
			                             ,ikyk(game,player,i.tgt)
										 ,game)
			if pred == "playing":
				i.bump(9)
			elif pred == "bombing":
				i.bump(-10)
			elif pred == "protective":
				i.bump(8)
			elif pred == "dud":
				i.bump(-10)
			#these ones are just not implemented yet...
			elif pred == "multi-play":
				i.bump(-10)
			elif pred == "stalling":
				i.bump(-10)
			
	return chs.sort()
	
def create_comp_tab(player):
	return deepcopy(player.trike.tab)
	
def pos_to_card(player,pos):
	for card in player.trike.tab.location[player.name]:
		if player.trike.tab.list[card].query_bit_pile(qquality="position",qvalue=pos):
			return card
	#convert a hand position into a card that can be 
	#used to create an Event

def event_from_choice(choice,player,game):
	if choice.action != "Clue":
		card_id = game.decks[player.name].deck[len(game.decks[player.name].deck)-choice.pos].id 	
	else:
		card_id = None
		
	return HanabiEvent(player,choice.tgt,choice.action,card_id,choice.color,choice.number)
	
class HanabiNPC(Player):
	def __init__(self,name,game):
		Player.__init__(self,name,game)

	def decision(self,game):
		return event_from_choice(eval_flow(self,game),self,game)
	
	def analysis(self):
		pass

class HanabiSimNPC(HanabiNPC):
	def __init__(self,name,game,N):
		HanabiNPC.__init__(self,name,game)
		self.depth = N
		self.fref = ".\\{}depth{}.hanabidata".format(name,self.depth)
	
	def im_a_dummy(self):
		if self.depth == game.total_depth:
			return True
		return False
	
	def im_with_stupid(self):
		if self.depth == game.total_depth-1:
			return True
		return False

class HanabiGame(object):
	def __init__(self,name,variant,conventions,deduction_bot,player_name_list,total_depth,depth):
		self.name = name
		self.total_depth = total_depth
		self.variant = variant
		self.colors = variant.colors
		self.numbers = variant.numbers
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
		self.bot = deduction_bot
		self.defeat = False
		self.victory = False
		self.final_countdown = 0
		self.card_list = {}
		self.initial_game_deck = {}
		self.decks = {}
		self.depth = depth
		self.set_game_deck()
		self.set_stacks()
		self.initial_player_order(player_name_list)
		self.update_all_tables()
		self.initial_hands()
		self.set_game_log()
	
	def __repr__(self):
		return self.name
	
	def set_game_deck(self):
		self.add_card_list(HanabiGameDeck("card_list",self.variant, self.variant.decktemplate))
		game_deck = HanabiGameDeck("game_deck",self.variant,self.variant.decktemplate)
		if self.depth == 0:
			game_deck.print_distr()
		game_deck.shuffle()
		initial_game_deck = deepcopy(game_deck)
		self.add_initial_game_deck(initial_game_deck)
		self.add_deck(game_deck)

	def set_stacks(self):
		self.add_deck(HanabiStacks("Play",self.variant,self.variant.stackstemplate))
		self.add_deck(HanabiStacks("Discard",self.variant,self.variant.stackstemplate))
		self.play = self.decks["Play"]
		self.discard = self.decks["Discard"]
		
	def add_deck(self,deck):
		self.decks[deck.name] = deck
	
	def add_initial_game_deck(self,initial_game_deck):
		self.initial_game_deck = initial_game_deck
	
	def add_card_list(self,card_list):
		self.card_list = card_list
	
	def set_game_log(self):
		#calculate maximum length of log
		NUM_PLAYS_TO_WIN = len(self.colors) * len(self.numbers)
		NUM_OF_FIVES = len(self.colors)
		INITIAL_CLOCKS = self.clocks
		INITIAL_DECK_SIZE = len(self.decks["game_deck"])
		NUM_PLAYERS = len(self.players)
		MAX_TURNS = NUM_PLAYS_TO_WIN + INITIAL_CLOCKS + NUM_OF_FIVES + 2*(INITIAL_DECK_SIZE - NUM_PLAYS_TO_WIN) - 1 + NUM_PLAYERS
		
		#initialize Future Log
		self.future_log = deque([HanabiEvent(None,None,None,None,None,None) for x in range(MAX_TURNS)])
		self.past_log = []
	
	def set_conventions(self,conventions):
		self.con = conventions
		for p in self.players:
			p.trike.set_conventions(self.con)
	
	def inc_clocks(self):
		self.clocks += 1
		
	def dec_clocks(self):
		self.clocks -= 1
	
	def bomb(self):
		self.bombs-=1
		if (self.bombs==0):
			self.defeat = True
	
	def inc_fc(self):
		self.final_countdown += 1
		
	def draw_card(self,deckname):
		return self.decks[deckname].draw()
		#table update occurs in Player
		
	def play_card(self,card,player):
		if self.bot.playable(card,self):
			for handcard in self.decks[player.name].deck:
				if handcard == card:
					idx = self.decks[player.name].deck.index(handcard)
					break
			self.play.add(self.decks[player.name].deck.pop(idx))
			#update tables
			for dude in self.players:
				dude.trike.tab.new_location(card,"Play",self)
			player.trike.tab.new_visible(card,"Play",self)
			
			if len(self.play) == 25:
				self.victory = True
		else:
			self.bomb()
			self.discard_card(card,player)	
		
	def discard_card(self,card,player):
		for handcard in self.decks[player.name].deck:
			if handcard == card:
				idx = self.decks[player.name].deck.index(handcard)
				break
		self.discard.add(self.decks[player.name].deck.pop(idx))
		#update tables
		for dude in self.players:
			dude.trike.tab.new_location(card,"Discard",self)
		player.trike.tab.new_visible(card,"Discard",self)
		
		
#TABLE FUNCTIONS
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

	def action(self,ev):
		#Figure out whodunit...
		for p in self.players:
			if p.name == ev.src:
				# and make em do it.
				if (ev.type == "Play" or ev.type == "Discard"):
					tempcard = Card(ev.id,ev.color,ev.number)
					# Figure out which card in their hand is used
					for card in self.decks[p.name].deck:
						if (card == tempcard):
							if ev.type == "Play":
								if self.depth == 0:	
									print("Attempting to play {}".format(tempcard))
								self.play_card(card,p)	
								if(ev.number==5 and tempcard in self.play.deck and self.clocks < self.MAX_CLOCKS):
									self.inc_clocks()
								p.draw(self,"game_deck")
								
							elif ev.type == "Discard":
								self.discard_card(card,p)
								if self.clocks < self.MAX_CLOCKS:
									self.inc_clocks()
								p.draw(self,"game_deck")
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
									print(" {}".format(len(self.decks[ev.tgt].deck) - self.decks[ev.tgt].deck.index(card)))
						elif ev.number:
							if (card.number == ev.number):
								# cards are printed to players in reverse order
								if self.depth == 0:
									print(" {}".format(len(self.decks[ev.tgt].deck) - self.decks[ev.tgt].deck.index(card)))
			elif p.name == ev.tgt:
				p.trike.bot.receive_clue(ev,p.trike.tab)
				p.trike.con.interpret_clue(ev,p.trike.tab,self)
		#Append the event to my own event log.
		self.past_log.append(ev)
	
	def add_player(self,dude):
		self.players.append(dude)
	
	def initial_player_order(self,player_name_list):
		npc_names = ["Platypus Bob", "Echidna Jane","Wallaby Jim"]
		npc_name_list = []
		if self.variant.playernum < len(player_name_list) +len(npc_name_list):
			print("Too many players for this variant.")
		while (self.variant.playernum > len(player_name_list) + len(npc_name_list)):
			npc_name_list.append(npc_names.pop())
		player_list =[]
		for name in player_name_list:
			player_list.append(Player(name,self))
		for name in npc_name_list:
			player_list.append(HanabiNPC(name,self))
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
		self.players_initial = deepcopy(self.players)
		self.bot.set_players(self.players_initial)
		for dude in self.players:
			dude.initialize_trike(self)
			self.decks[dude.name].print_distr()
	
	def initial_hands(self):
		for i in range(self.variant.handsize):
			for dude in self.players:
				dude.draw(self,"game_deck")
	
	def new_first_player(self):
		self.players.append(self.players.popleft())
	
	def update_all_tables(self):
		for dude in self.players:
			dude.trike.update_table(self)
	
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
					ws.write("***\n"+str(dude)+"'s hand: \n"+str(self.decks[dude.name])+"***\n\n")
				else:
					ws.write(str(dude)+"'s hand: \n"+str(self.decks[dude.name])+"\n")
		ws.write(str(self.play))
		ws.write(str(self.discard))
	
	def write_all_states(self):
		if self.depth == 0:
			print("Clocks: {}\n".format(self.clocks))
			print("Bombs: {}\n".format(self.bombs))		
			print("Cards in deck: {}\n\n".format(len(self.decks["game_deck"])))
			print(self.play)
			print(self.discard)
		for dude in self.players:
			self.write_state(dude)
	
class HanabiSim(HanabiGame):
	def __init__(self,name,game,sim_player_list,N):
		game_copy = deepcopy(game)
		self.deck_copy = deepcopy(game.initial_game_deck)
		super(HanabiSim,self).__init__(name,game_copy.variant,game_copy.con,game.bot,sim_player_list,game_copy.total_depth,N)
		
	def add_player(self,dude):
		self.players.append(dude)
	
	def set_game_deck(self):
		self.add_card_list(HanabiGameDeck("card_list",self.variant, self.variant.decktemplate))
		game_deck = self.deck_copy
		initial_game_deck = deepcopy(game_deck)
		self.add_initial_game_deck(initial_game_deck)
		self.add_deck(game_deck)
	
	def initial_player_order(self,player_name_list):
		player_list =[]
		for name in player_name_list:
			player_list.append(HanabiSimNPC(name,self,self.depth))

		for i in range(len(player_list)):
			self.add_player(player_list.pop(0)) #fed in in order of the real game
		self.players_initial = deepcopy(self.players)
		for dude in self.players:
			dude.initialize_trike(self)

class Tricorder(object):
	def __init__(self, game,player):
		self.name = player.name
		self.tab = BitTable(game,pl=player)
		self.bot = game.bot
		self.con = game.con
		
	def simulate(self,game,EventList,n):
		decision = self.decide(game)
		game.take_action(decision)		
		EventList.append(decision)
		if n==0:
			return
		else:
			return self.simulate(game,EventList,n-1)
	
	def set_conventions(self, conventions):
		self.con = conventions
	
	def run_sim(self,game,action,n):
		CurrentState = game.past_log
		game.take_action(action)
		EventList = [action]
		self.simulate(game,EventList,n)
		game.reset(CurrentState)
		return EventList
	
	def update_table(self,game):
		self.tab.update_location_list(game)
		self.tab.update_positions(game)
		self.tab.update_critical_list()
		self.bot.update_playability(self.tab,game)
		self.bot.update_discardability(self.tab)
		self.bot.update_color(self.tab)
		self.bot.update_number(self.tab)
		
	
	def decide(self):
		pass

class Knowledge(object): 
	def __init__(self,player,game,variant, future_log,past_log):
		self.player = player
		self.game = game
		self.variant = variant
		self.flog = future_log
		self.plog = past_log
		
class BitFolder(object):
	def __init__(self,game,card):
		self.types = ["confirmed","inkling","conventional","default"]
		self.qualities = ["color","number","location","playability","discardability","position"]
		self.values = {"color":game.colors,"number":game.numbers,"location":game.decks,"playability":["playable"],"discardability":["discardable"],"position":[x+1 for x in range(game.variant.handsize)]}
		self.spins = ["pos","neg","final","default"]
		self.folder = {quality:{value:[] for value in self.values[quality]} for quality in self.qualities}
		self.pile = []
		self.quality_pile = {quality:[] for quality in self.qualities}
		self.value_pile = {value:[] for quality in self.qualities for value in self.values[quality]}
		
	def __repr__(self):
		return str(self.pile)
	
	def add_bit(self,bit):
		self.folder[bit.quality][bit.value].append(bit)
		self.pile.append(bit)
		self.quality_pile[bit.quality].append(bit)
		self.value_pile[bit.value].append(bit)

	def remove_bit(self,bit):
		self.folder[bit.quality][bit.value].remove(bit)
		self.pile.remove(bit)
		self.quality_pile[bit.quality].remove(bit)
		self.value_pile[bit.value].remove(bit)
	
	def query_bit_pile(self,op="conj",qtype=[],qquality=[],qvalue=[],qspin=[]):	 # makes list of bits meeting criteria according to operator, input criteria as lists
		temp_list = []
		for bit in self.pile:
			bool_type = bit.type in qtype or not qtype
			bool_quality = bit.quality in qquality or not qquality
			bool_value = bit.value in qvalue or not qvalue
			bool_spin = bit.spin in qspin or not qspin
			if op == "conj":
				if (bool_type and bool_quality and bool_value and bool_spin):
					temp_list.append(bit)
			elif op == "disj":
				if ((bool_type and qtype)
				or (bool_quality and qquality)
				or (bool_value and qvalue)
				or (bool_spin and qspin)):
					temp_list.append(bit)
		return temp_list	
	
	def count_bits(self): #returns the size of the bit pile
		return len(self.pile)
	def count_bits(self,type,quality,value,spin): # returns number of bits meeting all criteria, input criteria as lists use [1] for "any"
		return len(self.query_bit_pile(type,quality,value,spin))
	
	def clear(self,ctype = None, cquality = None, cvalue = None, cspin = None):
		if (ctype and cspin):
			if (cquality):
				for bit in self.quality_pile[cquality][:]:
					if bit.type == ctype and bit.spin == cspin:
						self.remove_bit(bit)
			if (cvalue):
				for bit in self.value_pile[cvalue][:]:
					if bit.type == ctype and bit.spin == cspin:
						self.remove_bit(bit)
			return
		if (ctype):
			if (cquality):
				for bit in self.quality_pile[cquality][:]:
					if bit.type == ctype:
						self.remove_bit(bit)
				return
			if (cvalue):
				for bit in self.value_pile[cvalue][:]:
					if bit.type == ctype:
						self.remove_bit(bit)
				return
		if (cspin):
			if (cquality):
				for bit in self.quality_pile[cquality][:]:
					if bit.spin == cspin:
						self.remove_bit(bit)
				return
			if (cvalue):
				for bit in self.value_pile[cvalue][:]:
					if bit.spin == cspin:
						self.remove_bit(bit)
				return
		if (cvalue):
			for bit in self.value_pile[cvalue][:]:
				self.remove_bit(bit)
			return
		if (cquality):
			for bit in self.quality_pile[cquality][:]:
				self.remove_bit(bit)
			return
	#Again, left here in case of a mistake
	# def clear_quality(self,quality):
		
		# for bit in self.quality_pile[quality][:]:
			# self.remove_bit(bit)
	# def clear_quality(self,quality,type):
		# for bit in self.quality_pile[quality][:]:
			# if bit.type == type:
				# self.remove_bit(bit)

	# def clear_value(self,value):
		# for bit in self.value_pile[value]:
			# self.remove_bit(bit)
	# def clear_value(self,value,type):
		# for bit in self.value_pile[value]:
			# if bit.type == type:
				# self.remove_bit(bit)
		
class HanabiList(object):
	def __init__(self): #The thought here is to make counting and short_list assembly cleaner
		pass
		
class BitTable(object):
	def __init__(self,game,pl=None):  #May want to use id's for some of this?
		self.decktemplate = game.variant.decktemplate
		if pl:
			self.name = pl.name
		else:
			self.name = "None"
		self.list = {card: BitFolder(game,card) for card in game.decks["game_deck"].deck}
		self.location = {location.name: {card: self.list[card] for card in location.deck} 
		                                for deckname, location in game.decks.items()}
		self.known = {card: self.list[card] for card in self.list if self.fixed(card)}
		self.critical = {card: self.list[card]  for card in self.list if (self.only_one(card.color,card.number) and not self.gone(card))}
		self.play_q = deque([])
		if pl:
			self.discard_q = deque(deepcopy(game.decks[pl.name].deck))
		else:
			self.discard_q = deque([])
		#and other pre-organized lists of bit folders
		self.bit_counter = 0
	
	def inc_bit_counter(self):
		self.bit_counter += 1
		
	
	def add_bit(self,tail,card): #pin the tail to a card in the table	
		#only adds it if it isn't contradicted or made redundant by a confirmed bit
		x = self.list[card]
		folder = x.folder
		for bit in folder[tail.quality][tail.value]:
			#should only add bits with "final" spin when one isn't already there
			if bit.spin == "final":
				if tail.spin == "final":
					print("{}: Uh oh. This was already supposed to be final.".format(self.name))
					print(tail)
					return
				elif tail.spin == "neg":
					print("{}: Uh oh. This contradicts some final information.".format(self.name))
					print(tail)
					return
				else:
					print("{}: It was already final that this card is {}.".format(self.name,bit.value))
					return
			
			if bit.type == "confirmed":
				if tail.spin == "pos" and bit.spin == "neg":
					print("{}: Thought for a second that the card WAS {}  when in fact it was already NOT {}.".format(self.name,tail.value,bit.value))
					if tail.type == "inkling":
						print("But it was just an inkling.")
					return
				elif tail.spin == "neg" and bit.spin == "pos":
					print("{}: Thought for a second that the card was NOT {}  when in fact it was already WAS {}.".format(self.name,tail.value,bit.value))
					if tail.type == "inkling":
						print("But it was just an inkling.")
					return
				elif tail.spin == bit.spin:
					if tail.type == "inkling":
						if tail.spin == "pos":
							confirm_string = "IS"
						elif tail.spin == "neg":
							confirm_string = "is NOT"
						print("{}: Inkling already confirmed, this card {} {}.".format(self.name,confirm_string,tail.value))
						return
					if tail.type == "confirmed":
						if tail.spin == "pos":
							confirm_string = "IS"
						elif tail.spin == "neg":
							confirm_string = "is NOT"
						print("{}: I already confirmed that this card {} {}.".format(self.name,confirm_string,tail.value))
						return			
		#DO WE NEED ANY MORE SAFTETIES HERE??
		#Things like being rainbow when it's already negative for another color should be controlled by the game code/logic, not this mechanism
		#By now we feel safe to append, but first we: 
		#remove bits that are conflicting or redundant and less convincing
		if tail.spin == "final": #no other information about that quality is relevant
			x.clear(cquality = tail.quality)
		elif tail.type == "confirmed": #get rid of all inklings of the same value (more sophisticated things will have to be handled by deductions)
			x.clear(ctype ="inkling",cvalue = tail.value)
		x.add_bit(tail)
		self.inc_bit_counter()
	
	def gone(self,card):
		return (card in self.location["Play"] or card in self.location["Discard"])
	
	def dead(self,card):
		card_match = set([x for x in self.list if x.color==card.color and x.number==card.number])
		discarded_cards = set([x for x in self.location["Discard"]])
		return (card_match <= discarded_cards)
	
	def final(self,card,quality):
		for bit in self.list[card].quality_pile[quality]:
			if bit.type=="confirmed" and bit.spin == "final":
				return True
		return False

	def clued_cards(self,ev):
		if (ev.color):
			card_list = [card for card in self.location[ev.tgt] if card.color == ev.color]
		if (ev.number):
			card_list = [card for card in self.location[ev.tgt] if card.number == ev.number]
		return card_list
	
	def played(self,card):
		card_match = set([x for x in self.list if x.color==card.color and x.number==card.number])
		played_cards = set([x for x in self.location["Play"]])
		intersection = card_match & played_cards
		return (len(intersection)==1)
	
	def only_one(self,color,number):  #Needs embellishment, perhaps.  Might be the case that there are zero left.
		total = self.decktemplate.distr[color][number]
		gone_list = [card for card in self.list if (self.gone(card) and card.color == color and card.number == number)]
		number_left = total - len(gone_list)
		if number_left == 1:
			return True
		if number_left == 0:
			print("Just asked if a card that's already gone is the only_one.  You might want to change the list you loop over.")
		return False		
	
	
	def fixed(self,card):
		for bit in self.list[card].pile:
			if bit.spin == "final" and bit.quality == "color":
				for bit in self.list[card].pile:
					if bit.spin == "final" and bit.quality == "number":
						return True
		return False
		
	
	def new_position(self,card,player_name,game):	
		self.list[card].clear(cquality = "position")
		position = game.variant.handsize - game.decks[player_name].deck.index(card)
		Posbit = Hanabit("confirmed","position",position,"final",self)
		self.add_bit(Posbit,card)
		
	def update_positions(self,game):
		for card in self.list:
			in_some_hand = False
			for p in game.players:
				if card in self.location[p.name]:
					in_some_hand = True
					self.new_position(card,p.name,game)
			if (not in_some_hand):
				if self.list[card].query_bit_pile(qquality = ["position"], qspin = ["final"]):
					self.list[card].clear(cquality = "position")
			
			
	
	def new_location(self,card,location_name,game):
		if card in self.location[self.name]: #should already be done when card is played/discarded, but just in case
			if card in self.discard_q:
				self.discard_q.remove(card)
			if card in self.play_q:
				self.play_q.remove(card)
		self.list[card].clear(cquality = "location")
		Lbit = Hanabit("confirmed","location",location_name,"final",self)
		self.add_bit(Lbit,card)
		self.update_location_list(game)
		if location_name == self.name:
			if card not in self.discard_q:
				self.discard_q.append(card)	
			self.add_bit(Hanabit("default","discardability","discardable","default",self),card)
	
	def update_location_list(self,game):
		self.location = {location.name: {card: self.list[card] for card in location.deck} 
		                                for deckname, location in game.decks.items()}
	
	def update_critical_list(self):
		self.critical = {card: self.list[card]  for card in self.list if (self.only_one(card.color,card.number) and not self.gone(card))}
	
	def new_visible(self,card,location,game):
		if not self.final(card,"color"):
			color_bit = Hanabit("confirmed","color",card.color,"final",self)
			self.add_bit(color_bit,card)
		if not self.final(card,"number"):
			number_bit = Hanabit("confirmed","number",card.number,"final",self)
			self.add_bit(number_bit,card)
		self.new_location(card,location,game)
	
	def update_all_lists(self,game):
		self.update_location_list(game)
		self.update_critical_list()
		
	

	
	def make_short_list(self,type,quality,value,spin): #works like the make_pile in BitFolder
		temp_dict = {}
		for card in self.list:
			pile = self.list[card].pile
			for bit in pile:
				bool_type = bit.type in type or 1 in type
				bool_quality = bit.quality in quality or 1 in quality
				bool_value = bit.value in value or 1 in value
				bool_spin = bit.spin in spin or 1 in spin
				if (bool_type and bool_quality and bool_value and bool_spin):
					temp_dict[card] = self.list[card]
					break
		return temp_dict		
	#def make_short_dict(self,type,quality,value,spin,indices): #for cooler looping maybe someday
	
		
	def read_deck(self,name):
		pass		
		
	def tag(self,thing,type,quality,value,spin): 
		bit = Hanabit(type,quality,value,spin,self)
		self.list[thing].folder[quality][value].append(bit)

	def edit_bits(self):
		pass

	def update_knowledge(self):
		pass

class Choice(object):
	def __init__(self,action=None,tgt=None,color=None,number=None,pos=None):
		self.action = action
		self.tgt = tgt
		self.color = color
		self.number = number
		self.pos = pos
		self.score = 0
		
	def __lt__(self,other):
		return self.score < other.score
		
	def bump(self,by):
		self.score = self.score + by		

class Hanabit(object): # a single piece of information
	def __init__(self,knowledgeType,quality,value,spin,tab):
		self.tab = tab
		self.id = tab.bit_counter
		self.type = knowledgeType #confirmed,inkling,etc.
		self.quality = quality #color,number,protected, playable, discardable, etc.
		self.value = value #'R',3,True,etc.
		self.spin = spin #pos,neg,final (it is this thing to the exclusion of all others)	
		
	def __repr__(self):
		if self.quality == "location":
			output_str = self.quality[0:3]+":"+self.value
		elif self.quality == "number" or self.quality == "color":
			output_str = self.type[0:1].upper()+self.spin[0:1].upper()+" "+str(self.value)
		else:
			type_str = self.type[0:1].upper()
			quality_str = self.quality[0:3]
			value_str = str(self.value)
			spin_str = self.spin[0:1].upper()
			output_str = type_str+spin_str+" "+quality_str+":"+value_str
		return output_str		
	
	def __eq__(self,other):
		return (self.type == other.type and self.quality == other.quality and self.value == other.value and self.spin==other.spin)
	
	def __hash__(self):
		return hash((self.tab,self.id))	
# def all_known(self,value,table):
	# if value in self.decktemplate.colors:
		# value_list = {card:table.list[card] for card in table.list if card.color == value}
	# if value in self.decktemplate.numbers:
		# value_list = {card:table.list[card] for card in table.list if card.num == value}
	# for card in value_list:
		# if card not in table.known:
			# return False
	# return True
			
			
# def deduce_colors(self,game): ###  RAINBOW EDITION
	# for card in self.hand.c:
		# #Check if this is already done
		# for color in card.bits["color"]:
				# for bit in card.bits["color"][color]:
					# if bit.spin == "final" and bit.type == "confirmed":
						# continue
		# #If there is confirmed multiple color info, then it must be rainbow
		# if self.count_bits(self,card,"confirmed","color","any","pos") > 2:
			# Hbit=Hanabit("confirmed","color","H","final")
			# self.add_bit(HBit,card)
			# continue 
		# #If there is confirmed single color info, then rainbow has been eliminated and that info must be final.
		# if self.count_bits(self,card,"confirmed","color","any","pos") == 1:
			# for color in card.bits["color"]:
				# for bit in card.bits["color"][color]:
					# if bit.type == "confirmed":
						# Cbit = Hanabit("confirmed","color",bit.value,"final")
						# self.add_bit(CBit,card)
						# continue
		# #We can also deduce color by stacking negative information
		# color_set = set(deepcopy(game.colors))
		# #Continuing with this, we can also check to see what cards it cannot be given visible cards
		
		# #what else do we need here?
		# return