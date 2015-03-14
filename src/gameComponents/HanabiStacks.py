from src.gameComponents.Deck import Deck

__author__ = 'Matthew'




class HanabiStacks(Deck):
	# def __init__(self,name,vnt,template):
	# Deck.__init__(self,name,vnt)
	# self.name = name
	#self.distr = vnt.stackstemplate.distr
	#self.deck = self.build_deck()


	def __repr__(self):

		x = {a: [] for a in self.colors}
		for card in self.deck:
			x[card.color].append(card)

		y = ""
		y += "\n{} Stacks:\n".format(self.name)
		for i in x:
			y += str(x[i])
			y += "   "

		return y
