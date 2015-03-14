from src.gameComponents.Deck import Deck

__author__ = 'Matthew'




class HanabiHand(Deck):
	# def __init__(self,name,vnt,template):
	# Deck.__init__(self,name,vnt,template)
	# self.name = name
	#self.distr = vnt.handtemplate.distr
	#self.deck = self.build_deck()

	def __repr__(self):
		x = "   1 ---> {}\n".format(len(self.deck))
		for card in reversed(self.deck):
			x += str(card)
		x += "\n"
		return x