from src.gameComponents.HanabiDeckTemplate import HanabiDeckTemplate

__author__ = 'Matthew'



class HanabiVariant(object):
	def __init__(self, playernum, handsize, decktemplate, rules):
		self.playernum = playernum
		self.handsize = handsize
		self.clocks = 8
		self.bombs = 3
		self.colors = decktemplate.colors
		self.numbers = decktemplate.numbers
		self.decktemplate = decktemplate
		self.handtemplate = HanabiDeckTemplate(decktemplate.colors, decktemplate.numbers,
											   {x: {y: 0 for y in decktemplate.numbers} for x in decktemplate.colors})
		self.stackstemplate = HanabiDeckTemplate(decktemplate.colors, decktemplate.numbers,
												 {x: {y: 0 for y in decktemplate.numbers} for x in decktemplate.colors})
		self.rules = rules