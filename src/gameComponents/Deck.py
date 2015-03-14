__author__ = 'Matthew'

import random
import re
from src.gameComponents import Card


class Deck(object):
	def __init__(self, name, vnt, template, deckfile=None):
		self.colors = vnt.colors
		self.numbers = vnt.numbers
		self.name = name
		self.distr = template.distr
		if not deckfile:
			self.deck = self.build_deck()
		else:
			self.deck = self.build_deck_from_file(deckfile)

	def set_distr(self, distr):
		self.distr = distr

	def print_distr(self):
		print("{} distr:".format(self.name))
		r = ""
		for c in self.colors:
			for n, q in self.distr[c].items():
				if not (q == 0):
					r = r + "{}{}: {}  ".format(n, c, q)
			r = r + "\n"
		if not r.replace("\n", ""):
			print("Empty.\n")
		else:
			print(r)

	def build_deck(self):
		deck = []
		card_id = 1
		for color in self.distr:
			for num in self.distr[color]:
				for i in range(self.distr[color][num]):
					deck.append(Card(card_id, color, num))
					card_id += 1
		return deck

	def build_deck_from_file(self, deckfile):
		deck = []
		card_id = 1
		with open(deckfile) as fileref:
			for cl in fileref:
				m = re.search('^([12345])([BGRWY])$', cl)
				deck.append(Card(card_id, m.group(2), int(m.group(1))))
				card_id += 1
		print("Deck built from file {}.".format(deckfile))
		r = ""
		i = 0
		for card in deck:
			r = r + "{}: {} ".format(card.id, card)
			i += 1
			if (i % 10 == 0):
				r = r + "\n"
		if not r.replace("\n", ""):
			print("Empty.\n")
		else:
			print(r)
		return deck

	def shuffle(self):
		random.shuffle(self.deck)

	def draw(self):
		if (len(self.deck) == 0):
			print("Tried to draw from an empty deck.")
			return
		return self.deck.pop()

	def add(self, card):
		self.deck.append(card)

	def __len__(self):
		return len(self.deck)