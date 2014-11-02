#!/usr/bin/python           # This is client.py file

import socket
import re
import os
import time

HANABI_PORT = 7777
BUFFER_SIZE = 2048

class HanabiClient(object):
	def __init__(self):
		self.quit_client = False
		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		#self.s.settimeout(2)
		
	def print_header(self):
		print("############## HANABI ##############\n\n")
		
	def get_msg_from_server(self, s):
		msg = self.s.recv(BUFFER_SIZE).decode(encoding='UTF-8')
		print("Message received: {}".format(msg))
		size = len(msg)
		if (size == 0):
			print("IT WAS A SIZE 0 MESSSAAAAGGGGEEEE!!")
			return #there's no new data
		elif (msg == "HANABI:YOURTURN"):
			print("It is now your turn.")
		elif (msg == "HANABI:TURNUPD"):
			print("Here are the updates from the last turn.")
			
	def display_state(self):
		print("This is display_state\n")
		
	def send_user_response(self, s):
		print("This is send_user_response\n")

	def connect(self):
		while (True):
			#windows and unix have different clear screen commands
			os.system("cls" if os.name == "nt" else "clear")
			self.print_header()

			tryhost = input("What machine do you want to connect to?\n(Enter Q to quit)\n")
			if (tryhost.upper() == "Q"):
				self.quit_client = True
				break
			
			ipformat = re.compile(r"\d+\.\d+\.\d+\.\d+")
			if (not ipformat.match(tryhost)):
				print("That's not a valid IP address\n")
				time.sleep(3)
				continue
			
			self.s.connect((tryhost, HANABI_PORT)) #find out what exceptions this throws
			hostcheck = self.s.recv(BUFFER_SIZE).decode(encoding='UTF-8')
			if (hostcheck != "HANABISERVER"):
				print("Connected to a non-Hanabi server (server sent '{}')\n".format(hostcheck))
				time.sleep(3)
				self.s.close
				continue
			else:
				print("Connected to Hanabi server.")
				
			break
	
	def mainloop(self):
		while (not self.quit_client):
			self.get_msg_from_server(self.s)
			self.display_state()
			self.send_user_response(self.s)
			
			print("TEMP: Now quitting...\n")
			self.quit_client = True
			

		if (self.quit_client):
			self.s.close
			print("See ya next time.\n")
		
if (__name__ == "__main__"):
	cli = HanabiClient()
	cli.connect()
	cli.mainloop()
