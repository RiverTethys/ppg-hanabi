from collections import deque
import random
import re
from copy import deepcopy
from src.gameBits.BitTable import BitTable
from src.gameBits.Hanabit import Hanabit
from src.gameComponents.Choice import Choice
from src.gameComponents.HanabiEvent import HanabiEvent


def create_all_choices(player, game):
	allc = []
	# Create plays and discards
	p = [Choice(action="Play", pos=x + 1) for x in range(game.variant.handsize)]
	d = [Choice(action="Discard", pos=x + 1) for x in range(game.variant.handsize)]
	# Create clues
	c = []
	for pl in game.players:
		if pl.name != player.name:
			c = c + [Choice(action="Clue", tgt=pl.name, color=cl) for cl in game.colors if cl != "H"]
			c = c + [Choice(action="Clue", tgt=pl.name, number=nm) for nm in game.numbers if nm != 1000]
	allc = p + d + c
	return allc


def ikyk(game, playername, other):
	temptab = BitTable(game, pl=playername)
	temptab.update_location_list(game)
	temptab.update_critical_list()
	for card in game.play.deck:
		temptab.add_bit(Hanabit("confirmed", "color", card.color, "final", temptab), card)
		temptab.add_bit(Hanabit("confirmed", "number", card.number, "final", temptab), card)
	for card in game.discard.deck:
		temptab.add_bit(Hanabit("confirmed", "color", card.color, "final", temptab), card)
		temptab.add_bit(Hanabit("confirmed", "number", card.number, "final", temptab), card)
	for pl in game.players:
		for card in game.decks[pl.name].deck:
			if (pl.name != playername and pl.name != other):
				temptab.add_bit(Hanabit("confirmed", "color", card.color, "final", temptab), card)
				temptab.add_bit(Hanabit("confirmed", "number", card.number, "final", temptab), card)
	# Consult the log to find all clues given regarding
	# cards *currently* not visible to each of the two players.
	# Add only the content of those clues to the temp table
	# This will have to change when rainbow is added back in.
	for ev in game.past_log:
		if (ev.type == "Clue" and (ev.tgt == playername or ev.tgt == other)):
			game.bot.receive_clue(ev, temptab)
	game.con.order_play_q(temptab)
	game.con.order_discard_q(temptab)
	return temptab


def evaluate_choice(player, game, i):  # i is the choice
	clocks_are_low = (game.MAX_CLOCKS / 2) - game.clocks
	if i.action == "Play":
		i.bump(-(i.pos))
		c = pos_to_card(player, i.pos)
		if player.trike.tab.list[c].query_bit_pile(qtype=["confirmed"]
				, qquality=["playability"]
				, qvalue=["playable"]
				, qspin=["final"]):
			i.bump(18)
		elif player.trike.tab.list[c].query_bit_pile(qtype=["confirmed", "conventional"]
				, qquality=["playability"]
				, qvalue=["playable"]
				, qspin=["pos"]):
			i.bump(14)

	elif i.action == "Discard":
		c = pos_to_card(player, i.pos)
		i.bump(i.pos)
		if player.trike.tab.list[c].query_bit_pile(qtype=["default", "conventional", "confirmed"]
				, qquality=["discardability"]
				, qvalue=["discardable"]
				, qspin=["final", "pos", "default"]):

			if len(game.past_log) > game.variant.playernum:
				for num, card_in_q in enumerate(player.trike.tab.discard_q):
					if card_in_q == c:
						q_posit = num
						adjustment = - q_posit
						if clocks_are_low < 0:  ### seeing if this corrects the early discarding
							adjustment -= 9
						elif game.clocks == 1:
							adjustment += 1
						elif game.clocks == 0:
							adjustment += 3

						i.bump(adjustment)
				if c not in player.trike.tab.discard_q:
					i.bump(-5)
			else:
				i.bump(-10000)
		else:
			i.bump(-game.variant.handsize)

		# evaluate clues based on type of clue they'll think it is

	elif i.action == "Clue":
		if game.clocks > 0:
			if clocks_are_low < 0:
				i.bump(2)
			if game.clocks == 1:  ##mild disincentive to cluing when clues are very low
				i.bump(-1)
			pred = game.con.predict_clue(event_from_choice(i, player, game), ikyk(game, player.name, i.tgt), game)
			# print(i)
			# print(pred)
			if pred == "recently given":
				i.bump(-10)
			elif pred == "playing":
				i.bump(10)
			elif pred == "bombing":
				i.bump(-15)
			elif pred == "protective":
				i.bump(8)
			elif pred == "dud":
				i.bump(1)
			# these ones are just not implemented yet...
			elif pred == "multi-play":
				i.bump(-10)
			elif pred == "stalling":
				i.bump(-10)
		else:
			i.bump(-10000)


def narrow_choices(player, game, choices):
	pass


def evaluate_choices(player, game, i, i_string):  # i is the list of choices
	pass


def eval_flow(player, game):
	for p in game.players:
		p.trike.update_table(game)
	if game.depth == game.total_depth:
		return eval_flow_base_case(player, game)
	else:
		chs = create_all_choices(player, game)
		narrow_choices(player, game,
					   chs)  # this will provide a much-needed reduction in the number of simulations undertaken
		for choice in chs:
			event = event_from_choice(choice, player, game)
			EventList = [event]
			condition = save_condition(player, game)
			simulate(player, game, event, EventList)  # this will predict the events following a given choice
			evaluate_choices(player, game, choice, EventList)  # this will bump the choice
			reset_button(player, game, condition)
		chs.sort()
		# for x in chs:
		# print(x)
		return chs


def save_condition(player, game):
	pass


def reset_button(player, game, condition):
	pass


def simulate(player, game, event, EventList):
	for p in game.players:
		p.trike.update_table(game)

	game.action(event)

	event = player.nextplayer.decision(game.nextgame)

	EventList.append(event)
	if player.nextplayer.nextplayer:
		simulate(player.nextplayer, game.nextgame, event, EventList)
		return
	else:
		return


def eval_flow_base_case(player, game):
	chs = create_all_choices(player, game)
	# go through the hand. score playables, score others as discardable

	for i in chs:
		evaluate_choice(player, game, i)

	chs.sort()
	for x in chs:
		print(x)
	return chs


def create_comp_tab(player):
	return deepcopy(player.trike.tab)


def pos_to_card(player, pos):
	for card in player.trike.tab.location[player.name]:
		if player.trike.tab.list[card].query_bit_pile(qquality=["position"], qvalue=[pos]):
			return card
		# convert a hand position into a card that can be
		# used to create an Event


def event_from_choice(choice, player, game):
	if choice.action != "Clue":
		card_x = game.decks[player.name].deck[len(game.decks[player.name].deck) - choice.pos]
		choice.color = card_x.color
		choice.number = card_x.number
		card_id = card_x.id
	else:
		card_id = None

	return HanabiEvent(player.name, choice.tgt, choice.action, choice.pos, card_id, choice.color, choice.number)









class Knowledge(object):
	def __init__(self, player, game, variant, future_log, past_log):
		self.player = player
		self.game = game
		self.variant = variant
		self.flog = future_log
		self.plog = past_log




class HanabiList(object):
	def __init__(self):  # The thought here is to make counting and short_list assembly cleaner
		pass






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
