from miniboa import *

#define Hanabi connect and disconnect behavior
#required by miniboa

def _on_connect(client):
    """
    Placeholder new connection handler.
    """
    print("++ Opened connection to {}, sending greeting...".format(client.addrport()))
    client.send("HANABISERVER")
    print("++ DEBUG: greeting sent.")

def _on_disconnect(client):
    """
    Placeholder lost connection handler.
    """
    print("-- Lost connection to {}".format(client.addrport()))
	
#define Hanabi server
	
class HanabiServer(TelnetServer):
	def __init__(self):
		self.game_running = False
		super(HanabiServer,self).__init__(7777,'',_on_connect,_on_disconnect,0.01)

if __name__ == '__main__':
	SERVER_RUN = True
	GAME_SIZE = 2
			
	srv = HanabiServer()

	print(">> Listening for connections on port {}.  CTRL-C to break.".format(srv.port))

	## Server Loop
	while SERVER_RUN:
		srv.poll()        ## Send, Recv, and look for new connections
		if (srv.game_running):
			print("Game is running.")
			#check if the current player has submitted a move
			#make sure to flip game_running to False if everyone DCs
		elif (len(srv.clients) == GAME_SIZE):
			print("The game will start now.")
			#there are enough waiting players to start the game
		#else:
		#	print("Looping again...")

	print(">> Server shutdown.")