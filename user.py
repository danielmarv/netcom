import socket
import threading

# Server configuration
SERVER_HOST = 'your_server_ip'  # Replace with the IP address of the admin server
SERVER_PORT = 5555

# Create a socket to connect to the admin server
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
    client_socket.connect((SERVER_HOST, SERVER_PORT))

    def receive_messages():
        while True:
            # Receive and display messages from the admin
            message = client_socket.recv(1024).decode('utf-8')
            print(f"Received Message: {message}")

    # Start a separate thread to continuously receive messages
    threading.Thread(target=receive_messages, daemon=True).start()

    # The main thread can be used for user input or any other functionality

    # Example: Send a message to the admin
    while True:
        user_input = input("Enter your message: ")
        client_socket.sendall(user_input.encode('utf-8'))
