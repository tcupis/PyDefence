"""
Project: PyDefence
Author: Tom Cupis
Date started: 5/9/2018

"""

#* Imports/dependencies
#Standard libraries
import time
import random
import json
import socket
import string

#Required libraries
try:
    from data.pydefence import PyDefence
except:
    #Quit if failed
    raise


class GameServerInterface():
    #Object to store client-server interfacer

    def __init__(self, _ds, _bs=1024):
        #Initialise client variables
        self.ds = _ds
        self.active_server = _ds
        self.active_lobby = None
        self.buffer_size = _bs

        #Helper
        self.pyd = PyDefence()

        #Create a unique client ID
        self.client_id = self.generateHash(64)
        self.pyd.log(self.client_id)
        
        #Client constants
        self.EOMT_ID = "\EOMT;;" #end of msg transmission
        self.RETRY_DELAY = 2

        #Reset client variables
        self.resetServerInfo()
        self.resetRequest()
        self.resetMsg()
        
    def resetServerInfo(self):
        #Reset client's server information
        self.ping = "Not connected"
        self.all_lobbies = []
        
    def resetRequest(self):
        #Reset client request template
        self.client_request = {
            "game": "PYDEFENCE",
            "request": {
                "aim":"connect",
                "parameters": [],
            },
            "client_id": self.client_id,
            "lobby_id": self.active_lobby,
            "timestamp": time.time()
            }

    def resetMsg(self):
        #Reset client message
        self.new_msg = {
            "sender": None,
            "message": None
            }

    def generateHash(self, n):
        #Generate a random hash of length n
        return ''.join(random.choice(string.ascii_letters + string.digits) for i in range(n))

    def connect(self, server=None, max_retries=10):
        #Connect to a server
        if server == None: server = self.active_server
        
        #Create socket object
        self.SocketObject = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        #Start retry attempts
        current_retry = 0
        while current_retry < max_retries:
            #Reset server information
            self.resetServerInfo()

            #Connect using socket object
            try:
                self.SocketObject.connect(server)
                self.pyd.log("connected to "+str(server))
                self.resetRequest()
                self.send()
                return True

            except TimeoutError:
                #Handle timeout from server
                self.pyd.log("Timeout! retry attempt "+str(current_retry+1))

            except:
                #Handle other network errors
                self.pyd.log("Connection failed {} time(s)".format(current_retry+1))

            #Try again after increasing periods
            current_retry += 1
            time.sleep(self.RETRY_DELAY*current_retry)
        
        #If never connects return false
        return False
            
    def listen(self):
        #Listen for a server response
        try:
            server_response = ""

            #While the 'End of Message Transmission' isn't in the message still receive message from buffer
            while self.EOMT_ID not in server_response:
                server_response += self.SocketObject.recv(self.buffer_size).decode("utf-8")

                #If response is blank then server has disconnected
                if server_response == "": raise ConnectionAbortedError
                
            #Get dictionary from string response, minus the end of msg transmission ID
            server_response = json.loads(server_response[:-len(self.EOMT_ID)])
            self.pyd.log(server_response)

            #Return the server's message
            return server_response

        except:
            #Reconnect if server failed to connect
            self.SocketObject.close()
            self.start()

    def send(self):
        #Send a message to the server

        #! Validation
        #Check the message contents before sending
        if self.client_request["request"]["aim"] != None:
            #Try and send the message via the socket object
            try:
                self.pyd.log(self.client_request)
                self.SocketObject.send(str.encode(str(json.dumps(self.client_request))+self.EOMT_ID))
            except:
                #Handle errors by reconnecting
                self.SocketObject.close()
                self.connect()

    #* Preset requests
    def createGameLobby(self, parameters):
        #Create a create lobby request and send it
        self.resetRequest()
        self.client_request["request"]["aim"] = "create lobby"
        self.client_request["request"]["parameters"] = parameters #[map, diff, name]
        self.send()

    def joinGameLobby(self, lobby_id):
        #Create a join lobby request and send it
        self.resetRequest()
        self.client_request["request"]["aim"] = "join lobby"
        self.client_request["request"]["parameters"] = lobby_id
        self.send()

    def disconnectRequest(self):
        #Create a disconnect request and send it
        self.resetRequest()
        self.client_request["request"]["aim"] = "disconnect"
        self.send()

    def getLobbies(self):
        #Create a get lobbies request and send it
        self.resetRequest()
        self.client_request["request"]["aim"] = "get lobbies"
        self.send()

    def sendMsg(self, msg, client_name):
        #Create a send message request and send it with the client's message contained
        self.resetMsg()
        self.new_msg["sender"] = client_name
        self.new_msg["message"] = msg

        self.client_request["request"]["aim"] = "send msg"
        self.client_request["request"]["parameters"] = self.new_msg
        self.send()

    def confirmHandshake(self):
        #Sends a confirmation of the connection handshake allowing server communication
        self.resetRequest()
        self.client_request["request"]["aim"] = "confirm"
        self.send()

    #* Server management
    def start(self):
        #Connect to the server and call the server handler if successful
        if self.connect(self.active_server):
            self.serverHandler()

    def serverHandler(self):
        #Method to handle all communication after a successful handshake
        self.multiplayer_active = True

        #Respond to events indefinitely
        while self.multiplayer_active:
            reply = self.listen()
            changePing = True
            
            #Do different actions based off server response
            if reply["reply"] == "confirm handshake":
                self.confirmHandshake()
            
            elif reply["reply"] == "success":
                self.server_name = reply["server_name"]
                self.connected_players = reply["connected_clients"]
                self.getLobbies()

            elif reply["reply"] == "lobby details":
                self.active_lobby = reply["data"]

            elif reply["reply"] == "all lobbies":
                self.all_lobbies = reply["data"]
                changePing = False

            elif reply["reply"] == "new msg":
                self.new_msg = reply["data"]
                changePing = False

            else:
                #Handles unknown server communication
                self.pyd.log("Unknown server response! Is your game version up to date?")

            #Updates ping if appropriate
            if changePing:
                self.ping = reply["ping"]

        #Try and connect and repeat the cycle again
        self.start()
