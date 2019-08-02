"""
Project: PyDefence
Author: Tom Cupis
Date started: 5/9/2018

"""

#* Imports/dependencies
#Standard libraries
import tkinter as tk
import _thread as thr
import socket
import os
import time
import json
import random
import string

#Required libraries
try:
    import tkinter as tk
    import _thread as thr
    import configparser as cp
except:
    #Writing logs if import fails
    temp_file = open("FATAL-SERVER-LAUNCH-{}.txt".format(random.randint(0,10**10)), 'w')
    temp_file.write("A fatal launch error occurred, ensure you have the required packages\n\nGet required packages:\n\t-_thread\n\t-tkinter\n\t-configparser")
    temp_file.close()

    quit()

#Standard error dictionary
STANDARD_ERRORS = {
    "INVALID_RESPONSE": {
        "reply": "error - invalid response to server"
    },
    "UNKNOWN": {
        "reply": "error - an unknown error occurred"
    }
}

class DistributionServer():
    #Object to store all server tasks

    def __init__(self, _name, _addr):
        #Initialise server variables
        self.name = _name
        self.address = _addr
        self.active_lobbies = []
        self.BACKLOG_LEN = 64
        self.EOMT_ID = "\EOMT;;"
        self.buffer_size = 1024
        self.live = False
        self.clients = {}
        self.active_lobbies = {}

    def start(self):
        #Start the server and bind application to a socket object
        self.SocketObject = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        while not self.live:
            try:
                self.SocketObject.bind(self.address)
            except Exception as e:
                #Handles socket binding errors
                print("Server startup error: \n\t{}".format(e))

                #Retry server startup
                time.sleep(30)
                continue

            self.SocketObject.listen(self.BACKLOG_LEN) #queues connections

            print("Server started!", self.address)

            self.live = True

        #Handles pending connections in the queue starting threads for handshakes
        while self.live:
            ConnectionObject, address = self.SocketObject.accept()
            thr.start_new_thread(self.clientHandshake, (ConnectionObject, address))
    
    def generateHash(self, n):
        #Generates a random hash of length n
        return ''.join(random.choice(string.ascii_letters + string.digits) for i in range(n))

    def clientHandshake(self, ConnectionObject, address):
        #Client handshake procedure, any invalid steps causes a connection drop for that client
        try:
            #Receive client's request to connect
            client_data = ""
            while self.EOMT_ID not in client_data:
                client_data += ConnectionObject.recv(self.buffer_size).decode("utf-8")
                if client_data == "": raise ConnectionAbortedError
            client_data = json.loads(client_data[:-len(self.EOMT_ID)])
            client_id = client_data["client_id"]

            #Checks if aim of the connection is connect
            if client_data["request"]["aim"] == "connect":
                self.clients[str(client_id)] = {
                    "connection": ConnectionObject,
                    "address": address,
                    "last_timestamp": client_data["timestamp"],
                    "lobby": client_data["lobby_id"]
                }

                #Sends client a request to confirm connection
                handshake_json = {
                    "reply": "confirm handshake",
                    "ping": "? ms"

                }
                self.send(client_id, handshake_json)

                #! Validation
                #Validates the confirmation handshake
                client_data = self.listen(client_id)
                if client_data["request"]["aim"] == "confirm":
                    #Calculates a ping from handshake procedure
                    t1 = float(self.clients[client_id]["last_timestamp"])
                    t2 = float(client_data["timestamp"])

                    ping = (1000*(t2-t1))/3
                    if ping < 1:
                        ping = "<1ms"
                    else:
                        ping = "{:.3g}ms".format(ping)
                    
                    #Sends success message to client, allowing this client to communicate with the server
                    self.clients[str(client_id)]["last_timestamp"] = client_data["timestamp"] 
                    successful_json = {
                        "reply": "success",
                        "ping": ping,
                        "server_name": self.name,
                        "connected_clients": len(self.clients)
                    }

                    self.send(client_id, successful_json)

                    #Start game handler with client
                    self.gameHandler(client_id)
                else:
                    print(client_data, "expected 'confirm' aim")
                    raise ConnectionError


                print(str(address)+" connected")
            else:
                print(client_data, "expected 'connect' aim")
                raise ConnectionError

        except:
            print(str(address), "invalid handshake")
            
            #Remove invalid client as handshake was invalid
            try:self.clients.pop(client_id, None)
            except: pass

            ConnectionObject.close()

    def listen(self, client_id):
        client_response = ""

        #While the 'End of Message Transmission' isn't in the message still receive message from buffer
        while self.EOMT_ID not in client_response:
            client_response += self.clients[str(client_id)]["connection"].recv(self.buffer_size).decode("utf-8")
            
            #If response is blank then client has disconnected
            if client_response == "": raise ConnectionAbortedError

        #Get dictionary from string response, minus the end of msg transmission ID      
        client_response = json.loads(client_response[:-len(self.EOMT_ID)])

        #Return the client's message
        return client_response

    def send(self, client_id, data):
        #Send a message to the client
        if len(str(data)) > 0:
            self.clients[str(client_id)]["connection"].send(str.encode(str(json.dumps(data)+self.EOMT_ID)))

    def gameHandler(self, client_id):
        #Client game handler, manages client requests to the server

        try:
            disconnected = False
            while not disconnected:
                #Listen to client response
                client_data = self.listen(client_id)

                #Calculate ping since last message
                t1 = float(self.clients[client_id]["last_timestamp"])
                t2 = float(client_data["timestamp"])

                ping = (1000*(t2-t1))/3
                if ping < 1:
                    ping = "<1ms"
                else:
                    ping = "{:.3g}ms".format(ping)
                
                #Record last communication
                self.clients[str(client_id)]["last_timestamp"] = client_data["timestamp"] 
                

                #Handle client aims
                if client_data["request"]["aim"] == "create lobby":
                    #Generate a lobby hash
                    lobby_id = self.generateHash(64)
                    try:
                        #Create lobby including hash
                        self.active_lobbies[lobby_id] = {
                            "lobby_id": lobby_id,
                            "clients_connected": [
                                client_data["client_id"]
                                ],
                            "map": client_data["request"]["parameters"][0],
                            "difficulty": client_data["request"]["parameters"][1],
                            "name": client_data["request"]["parameters"][2],
                            "time_created": client_data["timestamp"]
                        }
                    except:
                        #Handle invalid lobby creation requests
                        self.send(client_id, STANDARD_ERRORS["INVALID_RESPONSE"])

                    #Link client ID to lobby ID
                    self.clients[client_data["client_id"]]["lobby"] = self.active_lobbies[lobby_id]

                    #Send lobby details
                    lobby_json = {
                        "reply": "lobby details",
                        "ping": ping,
                        "data": self.active_lobbies[lobby_id]
                    }

                    self.send(client_id, lobby_json)

                elif client_data["request"]["aim"] == "get lobbies":
                    #Send all lobbies online
                    lobbies_json = {
                        "reply": "all lobbies",
                        "ping": ping,
                        "data": self.active_lobbies
                    }

                    self.send(client_id, lobbies_json)

                elif client_data["request"]["aim"] == "join lobby":
                    #Link client to lobby requested
                    lobby_json = {
                        "reply": "lobby details",
                        "ping": ping,
                        "data": self.active_lobbies[client_data["request"]["parameters"]]
                    }
                    self.clients[client_data["client_id"]]["lobby"] = self.active_lobbies[client_data["request"]["parameters"]]
                    self.active_lobbies[client_data["request"]["parameters"]]["clients_connected"].append(client_data["client_id"])
                    self.send(client_id, lobby_json)

                elif client_data["request"]["aim"] == "disconnect":
                    #Handle disconnects
                    disconnected = True

                elif client_data["request"]["aim"] == "send msg":
                    #Send message to all clients inside a lobby
                    msg = client_data["request"]["parameters"]
                    
                    msg_json = {
                        "reply": "new msg",
                        "ping": ping,
                        "data": msg
                    }

                    clients_in_lobby = self.clients[client_data["client_id"]]["lobby"]["clients_connected"]
                    
                    for client in clients_in_lobby:
                        self.send(client, msg_json)

                else:
                    #Handle invalid aims
                    self.send(client_id, STANDARD_ERRORS["INVALID_RESPONSE"])


        except:
            pass
            
        #Handle client disconnects/errors
        print(str(self.clients[str(client_id)]["address"])+" disconnected")
        

        #If lobby is empty remove it
        self.active_lobbies[self.clients[client_id]["lobby"]["lobby_id"]]["clients_connected"].remove(client_id)
        if len(self.active_lobbies[self.clients[client_id]["lobby"]["lobby_id"]]["clients_connected"]) == 0:
            self.active_lobbies.pop(self.clients[client_id]["lobby"]["lobby_id"], None)

        #Close connection
        self.clients[str(client_id)]["connection"].close()
        self.clients.pop(str(client_id), None)
        
        

class ServerGUI():
    def __init__(self):
        #Get server config settings
        parser = cp.ConfigParser()
        parser.read('server/server.cfg')

        server_name = parser.get('settings', 'server_name')

        #Create server object
        self.ds = DistributionServer(server_name, ("localhost", 1000))
        self.root = tk.Tk()

        #Server UI
        self.root.resizable(0,0)
        self.root.attributes("-topmost", parser.get('settings', 'window_topmost'))
        self.root.title("PYD Server Manager | {}".format(self.ds.name))


        tk.Frame(self.root, width=600, height=10).grid(row=0, column=0, columnspan=3, sticky=tk.N)

        self.status_bar = tk.Frame(self.root, bg="grey", width=600, height=3)
        self.status_bar.grid(row=0, column=0, columnspan=3, sticky=tk.N)
        
        tk.Label(self.root, text="Clients connected").grid(row=1, column=0)
        self.clients_ds = tk.Listbox(self.root, width=25, height=30)
        self.clients_ds.grid(row=2, column=0)
        self.total_clients_ds = tk.Label(self.root, text="Total: 0")
        self.total_clients_ds.grid(row=3, column=0)

        tk.Label(self.root, text="Clients in-game").grid(row=1, column=1)
        self.clients_game = tk.Listbox(self.root, width=40, height=30)
        self.clients_game.grid(row=2, column=1)
        self.total_clients_game = tk.Label(self.root, text="Total: 0")
        self.total_clients_game.grid(row=3, column=1)

        tk.Label(self.root, text="Lobby Servers").grid(row=1, column=2)
        self.lobbies_live = tk.Listbox(self.root, width=30, height=30)
        self.lobbies_live.grid(row=2, column=2)
        self.total_lobbies = tk.Label(self.root, text="Total: 0")
        self.total_lobbies.grid(row=3, column=2)


        #Launch variable monitor
        thr.start_new_thread(self.guiManager, ())
        
    def guiManager(self):
        #Start server
        thr.start_new_thread(self.ds.start, ())

        #While the program is live update the UI with the state of the variables
        while True:

            #Update status label
            if self.ds.live:
                self.status_bar.config(bg="limegreen")
            else:
                self.status_bar.config(bg="red")

            #Clear listboxes
            self.clients_ds.delete(0, tk.END)
            self.clients_game.delete(0, tk.END)
            self.lobbies_live.delete(0, tk.END)

            try:
                #Populate active lobbies
                for lobby in self.ds.active_lobbies:
                    self.lobbies_live.insert(tk.END, self.ds.active_lobbies[lobby]["name"]+" | clients:"+str(len(self.ds.active_lobbies[lobby]["clients_connected"])))


                self.total_lobbies.config(text="Total: {}".format(len(self.ds.active_lobbies)))

                #Populate clients in game
                tc_in_game = 0
                for lobby in self.ds.active_lobbies:
                    if len(self.ds.active_lobbies[lobby]["clients_connected"]) != 0:
                        for client in self.ds.active_lobbies[lobby]["clients_connected"]:
                            try:
                                self.clients_game.insert(tk.END, str(self.ds.clients[client]["address"])+" in "+str(self.ds.active_lobbies[lobby]["name"]))
                            except KeyError:
                                pass
                            tc_in_game += 1

                self.total_clients_game.config(text="Total: {}".format(tc_in_game))

                #Populate clients in DS
                for client in self.ds.clients:
                    try:
                        self.clients_ds.insert(tk.END, self.ds.clients[client]["address"])
                    except KeyError:        
                        pass
                    
                
                self.total_clients_ds.config(text="Total: {}".format(len(self.ds.clients)))


            except:
                #Handle unknown errors
                pass

            #Rate limiter
            time.sleep(1)

# Main program
app = ServerGUI()
app.root.mainloop()


