#!/usr/bin/python           # This is client.py file

import socket
import re
import os
import time

s = socket.socket()

valid_connect = False
quit_client = False
HANABI_PORT = 64651
BUFFER_SIZE = 1024
		
def print_header():
	print("############## HANABI ############\n\n")
	
def get_prompt_from_server():
	print("This is get_prompt_from_server\n")
	
def display_state():
	print("This is display_state\n")
	
def send_user_response():
	print("This is send_user_response\n")

while (not valid_connect):
	#windows and unix have different clear screen commands
	os.system("cls" if os.name == "nt" else "clear")
	print_header()

	tryhost = input("What machine do you want to connect to?\n(Enter Q to quit)\n")
	if (tryhost.upper() == "Q"):
		quit_client = True
		break
	
	ipformat = re.compile(r"\d+\.\d+\.\d+\.\d+")
	if (not ipformat.match(tryhost)):
		print("That's not a valid IP address\n")
		time.sleep(3)
		continue
	
	s.connect((tryhost, HANABI_PORT)) #find out what exceptions this throws
	hostcheck = s.recv(BUFFER_SIZE).decode(encoding='UTF-8')
	if (hostcheck != "HANABISERVER"):
		print("Connected to a non-Hanabi server (server sent {})\n".format(hostcheck))
		time.sleep(3)
		s.close
		continue
		
	valid_connect = True
	
while (not quit_client):
	get_prompt_from_server()
	display_state()
	send_user_response()
	
	print("TEMP: Now quitting...\n")
	quit_client = True
	

if (quit_client):
	s.close
	print("See ya next time.\n")
