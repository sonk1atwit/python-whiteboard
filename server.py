import socket
import threading
import json
import pickle

class WhiteboardServer:
    def __init__(self, host='localhost', port=5000):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen()
        
        self.clients = []
        self.drawings = []
        print(f"Server running on {host}:{port}")
        
    def broadcast(self, message, sender=None):
        for client in self.clients:
            if client != sender:
                try:
                    client.send(pickle.dumps(message))
                except:
                    self.clients.remove(client)
    
    def handle_client(self, client):
        while True:
            try:
                message = pickle.loads(client.recv(2048))
                if message["type"] == "drawing":
                    self.drawings.append(message["data"])
                    self.broadcast(message, client)
            except:
                self.clients.remove(client)
                client.close()
                break
    
    def start(self):
        while True:
            client, address = self.server.accept()
            print(f"Connected with {address}")
            
            # Send existing drawings to new client
            if self.drawings:
                client.send(pickle.dumps({
                    "type": "init",
                    "data": self.drawings
                }))
            
            self.clients.append(client)
            thread = threading.Thread(target=self.handle_client, args=(client,))
            thread.start()