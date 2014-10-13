import random

class Card(object):
	def __init__(self,id,number,color):
		self.id = id
		self.num = number
		self.color = color
	
	def __repr__(self):
		return str(self.num) + self.color + " "

	def __str__(self):	
		return str(self.num) + self.color + " "

class Deck(object):
	def __init__(self,name,vnt):
		self.colors  = vnt.colors
		self.values = vnt.values
		self.name = name
		self.distr = {}
		self.deck = self.build_deck()
		
		
	def set_distr(self,distr):
		self.distr = distr
	
	def print_distr(self):
		print("{} distr:  ".format(self.name)+str(self.distr))
		
	def build_deck(self):
		self.print_distr()
		deck = []
		card_id = 0	
		for color in self.distr:
			for num in self.distr[color]:
				for i in range(self.distr[color][num]):
					deck.append(Card(card_id,num,color))
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