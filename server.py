import socket
import threading
import json

class WhiteboardServer:
    def __init__(self, host='localhost', port=5000):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen()
        
        self.clients = []
        self.drawings = []
        self.clients_lock = threading.Lock()
        self.drawings_lock = threading.Lock()
        print(f"Server running on {host}:{port}")
    
    def send_message(self, client, data):
        """Serialize and send a message with a length prefix."""
        try:
            message = json.dumps(data)
            message_length = f"{len(message):<10}"  # 10-character length prefix
            client.sendall(message_length.encode('utf-8') + message.encode('utf-8'))
        except Exception as e:
            print(f"Error sending message to client: {e}")
            with self.clients_lock:
                if client in self.clients:
                    self.clients.remove(client)
            client.close()
    
    def receive_full_message(self, client):
        """Receive a complete message with a length prefix."""
        try:
            # Receive message length
            message_length_data = b""
            while len(message_length_data) < 10:
                packet = client.recv(10 - len(message_length_data))
                if not packet:
                    return None  # Connection closed
                message_length_data += packet
            message_length = int(message_length_data.decode('utf-8').strip())
            
            # Receive the actual message
            data = b""
            while len(data) < message_length:
                packet = client.recv(message_length - len(data))
                if not packet:
                    return None  # Connection closed
                data += packet
            message = json.loads(data.decode('utf-8'))
            return message
        except Exception as e:
            print(f"Error receiving message: {e}")
            return None
    
    def broadcast(self, message, sender=None):
        """Send a message to all clients except the sender."""
        with self.clients_lock:
            for client in self.clients:
                if client != sender:
                    self.send_message(client, message)
    
    def handle_client(self, client):
        while True:
            message = self.receive_full_message(client)
            if message is None:
                print("Client disconnected")
                with self.clients_lock:
                    if client in self.clients:
                        self.clients.remove(client)
                client.close()
                break
            if message["type"] == "drawing":
                data = message["data"]
                action = data.get("action")
                with self.drawings_lock:
                    if action == "clear":
                        self.drawings.clear()
                    else:
                        self.drawings.append(data)
                self.broadcast(message, sender=client)
    
    def start(self):
        while True:
            client, address = self.server.accept()
            print(f"Connected with {address}")
            
            # Send existing drawings to new client
            with self.drawings_lock:
                if self.drawings:
                    init_message = {
                        "type": "init",
                        "data": self.drawings
                    }
                    self.send_message(client, init_message)
            
            with self.clients_lock:
                self.clients.append(client)
            thread = threading.Thread(target=self.handle_client, args=(client,))
            thread.daemon = True
            thread.start()
