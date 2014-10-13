#!/usr/bin/env python
#------------------------------------------------------------------------------
#   chat_demo.py
#   Copyright 2009 Jim Storch
#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain a
#   copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.
#------------------------------------------------------------------------------

"""
Chat Room Demo for Miniboa.
"""

from miniboa import TelnetServer

IDLE_TIMEOUT = 300
CLIENT_LIST = []
SERVER_RUN = True


def on_connect(client):
    """
    Sample on_connect function.
    Handles new connections.
    """
    print("++ Opened connection to {}".format(client.addrport()))
    broadcast('{} joins the conversation.\n'.format(client.addrport() ))
    CLIENT_LIST.append(client)
    client.send("Welcome to the Chat Server, {}.\n".format(client.addrport() ))


def on_disconnect(client):
    """
    Sample on_disconnect function.
    Handles lost connections.
    """
    print("-- Lost connection to {}".format(client.addrport()))
    CLIENT_LIST.remove(client)
    broadcast('{} leaves the conversation.\n'.format(client.addrport() ))


def kick_idle():
    """
    Looks for idle clients and disconnects them by setting active to False.
    """
    ## Who hasn't been typing?
    for client in CLIENT_LIST:
        if client.idle() > IDLE_TIMEOUT:
            print("-- Kicking idle lobby client from {}".format(client.addrport()))
            client.active = False


def process_clients():
    """
    Check each client, if client.cmd_ready == True then there is a line of
    input available via client.get_command().
    """
    for client in CLIENT_LIST:
        if client.active and client.cmd_ready:
            ## If the client sends input echo it to the chat room
            chat(client)


def broadcast(msg):
    """
    Send msg to every client.
    """
    for client in CLIENT_LIST:
        client.send(msg)


def chat(client):
    """
    Echo whatever client types to everyone.
    """
    global SERVER_RUN
    msg = client.get_command()
    print('{} says, "{}"'.format(client.addrport(), msg))

    for guest in CLIENT_LIST:
        if guest != client:
            guest.send('{} says, {}\n'.format(client.addrport(), msg))
        else:
            guest.send('You say, {}\n'.format(msg))

    cmd = msg.lower()
    ## bye = disconnect
    if cmd == 'bye':
        client.active = False
    ## shutdown == stop the server
    elif cmd == 'shutdown':
        SERVER_RUN = False


#------------------------------------------------------------------------------
#       Main
#------------------------------------------------------------------------------

if __name__ == '__main__':

    ## Simple chat server to demonstrate connection handling via the
    ## async and telnet modules.

    ## Create a telnet server with a port, address,
    ## a function to call with new connections
    ## and one to call with lost connections.

    telnet_server = TelnetServer(
        port=7777,
        address='',
        on_connect=on_connect,
        on_disconnect=on_disconnect,
        timeout = .05
        )

    print(">> Listening for connections on port {}.  CTRL-C to break.".format(telnet_server.port))

    ## Server Loop
    while SERVER_RUN:
        telnet_server.poll()        ## Send, Recv, and look for new connections
        kick_idle()                 ## Check for idle clients
        process_clients()           ## Check for client input

    print(">> Server shutdown.")
