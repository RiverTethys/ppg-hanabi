from miniboa import *

#define Hanabi connect and disconnect behavior
#required by miniboa

def _on_connect(client):
    """
    Placeholder new connection handler.
    """
    print("++ Opened connection to {}, sending greeting...".format(client.addrport()))
    client.send("HANABISERVER")

def _on_disconnect(client):
    """
    Placeholder lost connection handler.
    """
    print("-- Lost connection to {}".format(client.addrport()))
	
#define Hanabi server
	
class HanabiServer(TelnetServer):
	def tst_confirm():
		print("This is a Hanabi server")

if __name__ == '__main__':
	SERVER_RUN = True
			
	srv = HanabiServer(7777,'',_on_connect,_on_disconnect,0.01)

	print(">> Listening for connections on port {}.  CTRL-C to break.".format(srv.port))

	## Server Loop
	while SERVER_RUN:
		srv.poll()        ## Send, Recv, and look for new connections

	print(">> Server shutdown.")