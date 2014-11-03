

#####################################################

	

from HanabiDeductionFlows import *
from HanabiConventionFlows import *

from collections import deque
import random



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
		
class HanabiEvent(object):
	def __init__(self,src,tgt,type,id,color,number):
		self.src = src
		self.tgt = tgt
		self.type = type # "Play", "Discard", or "Clue"
		self.id = id
		self.color = color
		self.number = number

		
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
			
			if len(self.play) == 25: #need to change this to reference a value based on the variant
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
		


class HanabiNPC(Player):
	def __init__(self,name,game):
		Player.__init__(self,name,game)

	def decision(self,game):
		last_card = game.decks[self.name].deck[0]
		event = HanabiEvent(self.name,None,"Discard",last_card.id,last_card.color,last_card.number)
		return event
	
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
		self.tab = BitTable(game,player)
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
	def __init__(self,game,player):  #May want to use id's for some of this?
		self.decktemplate = game.variant.decktemplate
		self.name = player.name
		self.list = {card: BitFolder(game,card) for card in game.decks["game_deck"].deck}
		self.location = {location.name: {card: self.list[card] for card in location.deck} 
		                                for deckname, location in game.decks.items()}
		self.known = {card: self.list[card] for card in self.list if self.fixed(card)}
		self.critical = {card: self.list[card]  for card in self.list if (self.only_one(card.color,card.number) and not self.gone(card))}
		self.play_q = deque([])
		self.discard_q = deque(deepcopy(game.decks[player.name].deck))
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
					print("Uh oh. This was already supposed to be final.")
					print(tail)
					return
				elif tail.spin == "neg":
					print("Uh oh. This contradicts some final information.")
					print(tail)
					return
				else:
					print("It was already final that this card is {}.".format(bit.value))
					return
			
			if bit.type == "confirmed":
				if tail.spin == "pos" and bit.spin == "neg":
					print("Thought for a second that the card WAS {}  when in fact it was already NOT {}.".format(tail.value,bit.value))
					if tail.type == "inkling":
						print("But it was just an inkling.")
					return
				elif tail.spin == "neg" and bit.spin == "pos":
					print("Thought for a second that the card was NOT {}  when in fact it was already WAS {}.".format(tail.value,bit.value))
					if tail.type == "inkling":
						print("But it was just an inkling.")
					return
				elif tail.spin == bit.spin:
					if tail.type == "inkling":
						if tail.spin == "pos":
							confirm_string = "IS"
						elif tail.spin == "neg":
							confirm_string = "is NOT"
						print("Inkling already confirmed, this card {} {}.".format(confirm_string,tail.value))
						return
					if tail.type == "confirmed":
						if tail.spin == "pos":
							confirm_string = "IS"
						elif tail.spin == "neg":
							confirm_string = "is NOT"
						print("I already confirmed that this card {} {}.".format(confirm_string,tail.value))
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
				if self.list[card].query_bit_pile(qcard = card,qquality = ["position"], qspin = ["final"]):
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
	
	def new_visible(self,card,location,game):
		if not self.final(card,"color"):
			color_bit = Hanabit("confirmed","color",card.color,"final",self)
			self.add_bit(color_bit,card)
		if not self.final(card,"number"):
			number_bit = Hanabit("confirmed","number",card.number,"final",self)
			self.add_bit(number_bit,card)
		self.new_location(card,location,game)
	
	def update_all_lists(self):
		pass
	

	
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
		




		

#FROM HERE ON, WE HAVE AI STUFFY STUFF

class Knowledge(object):
	def __init__(self,player,players):
		self.player = player
		hands = {}
		for dude in players:
			hands[dude] = read_deck(dude.name)
	
	

class Flow(object): #don't even know if this will remotely work out
	def __init__(self,type,subtype,game):
		self.type=type
		self.subtype=subtype