from server import WhiteboardServer
from client import WhiteboardClient
import sys

def main():
    print("Whiteboard Application")
    print("1. Start Server")
    print("2. Start Client")
    
    choice = input("Enter your choice (1 or 2): ")
    
    if choice == "1":
        print("Starting server...")
        server = WhiteboardServer(host='0.0.0.0', port=5000)
        server.start()
    elif choice == "2":
        print("Starting client...")
        # You can modify the host and port here if needed
        client = WhiteboardClient()
        client.run()
    else:
        print("Invalid choice. Please enter 1 or 2.")

if __name__ == "__main__":
    main()