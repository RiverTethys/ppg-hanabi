#!/usr/bin/python           # This is server.py file

import socket               # Import socket module

s = socket.socket()         # Create a socket object
#host = socket.gethostname() # Get local machine name
host = "127.0.0.1"
port = 64651                # Reserve a port for your service.
s.bind((host, port))        # Bind to the port

s.listen(5)                 # Now wait for client connection.
while True:
   c, addr = s.accept()     # Establish connection with client.
   print("Got connection from {}".format(addr))
   hanabiconfirm = "HANABISERVER".encode("UTF-8")
   c.send(hanabiconfirm)
   c.close()                # Close the connection
   break