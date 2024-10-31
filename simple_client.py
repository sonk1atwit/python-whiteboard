import tkinter as tk
from tkinter import colorchooser, messagebox
import socket
import threading
import pickle

class WhiteboardClient:
    def __init__(self, host, port=5000):
        self.root = tk.Tk()
        self.root.title("Collaborative Whiteboard")
        
        try:
            # Connect to server
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.connect((host, port))
            
            # Setup canvas
            self.canvas = tk.Canvas(self.root, width=800, height=600, bg='white')
            self.canvas.pack(expand=tk.YES, fill=tk.BOTH)
            
            # Drawing variables
            self.current_color = 'black'
            self.line_width = 2
            self.drawing = False
            self.last_x = None
            self.last_y = None
            
            # Control panel
            control_frame = tk.Frame(self.root)
            control_frame.pack(pady=5)
            
            # Color picker button
            color_btn = tk.Button(control_frame, text="Choose Color", command=self.choose_color)
            color_btn.pack(side=tk.LEFT, padx=5)
            
            # Clear button
            clear_btn = tk.Button(control_frame, text="Clear Canvas", command=self.clear_canvas)
            clear_btn.pack(side=tk.LEFT, padx=5)
            
            # Bind mouse events
            self.canvas.bind('<Button-1>', self.start_drawing)
            self.canvas.bind('<B1-Motion>', self.draw)
            self.canvas.bind('<ButtonRelease-1>', self.stop_drawing)
            
            # Start receiving thread
            thread = threading.Thread(target=self.receive_data)
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            messagebox.showerror("Connection Error", 
                               f"Could not connect to the whiteboard server.\nMake sure the server is running and try again.")
            self.root.destroy()
            return
    
    def choose_color(self):
        color = colorchooser.askcolor(title="Choose color")[1]
        if color:
            self.current_color = color
    
    def clear_canvas(self):
        self.canvas.delete("all")
        self.client.send(pickle.dumps({
            "type": "drawing",
            "data": {"action": "clear"}
        }))
    
    def start_drawing(self, event):
        self.drawing = True
        self.last_x = event.x
        self.last_y = event.y
    
    def draw(self, event):
        if self.drawing:
            x, y = event.x, event.y
            if self.last_x and self.last_y:
                self.canvas.create_line(
                    self.last_x, self.last_y, x, y,
                    fill=self.current_color,
                    width=self.line_width
                )
                self.client.send(pickle.dumps({
                    "type": "drawing",
                    "data": {
                        "action": "line",
                        "start": (self.last_x, self.last_y),
                        "end": (x, y),
                        "color": self.current_color,
                        "width": self.line_width
                    }
                }))
            self.last_x = x
            self.last_y = y
    
    def stop_drawing(self, event):
        self.drawing = False
        self.last_x = None
        self.last_y = None
    
    def receive_data(self):
        while True:
            try:
                message = pickle.loads(self.client.recv(2048))
                if message["type"] == "drawing":
                    data = message["data"]
                    if data["action"] == "clear":
                        self.canvas.delete("all")
                    elif data["action"] == "line":
                        self.canvas.create_line(
                            data["start"][0], data["start"][1],
                            data["end"][0], data["end"][1],
                            fill=data["color"],
                            width=data["width"]
                        )
            except:
                messagebox.showerror("Connection Lost", 
                                   "Lost connection to the whiteboard server.")
                self.root.destroy()
                break

def main():
    # Create a simple connection window
    connection_window = tk.Tk()
    connection_window.title("Connect to Whiteboard")
    connection_window.geometry("300x150")
    
    tk.Label(connection_window, text="Enter Server IP:").pack(pady=10)
    ip_entry = tk.Entry(connection_window)
    ip_entry.insert(0, "localhost")  # Default value
    ip_entry.pack(pady=5)
    
    def connect():
        host = ip_entry.get()
        connection_window.destroy()
        client = WhiteboardClient(host)
        client.root.mainloop()
    
    tk.Button(connection_window, text="Connect", command=connect).pack(pady=20)
    connection_window.mainloop()

if __name__ == "__main__":
    main()