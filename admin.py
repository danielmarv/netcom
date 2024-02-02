import socket

# Server configuration
HOST = '0.0.0.0'  # Listen on all available interfaces
PORT = 5555

# Create a socket to listen for incoming connections
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    server_socket.bind((HOST, PORT))
    server_socket.listen()

    print(f"Admin Server listening on {HOST}:{PORT}")

    # Accept incoming connections
    conn, addr = server_socket.accept()

    with conn:
        print(f"Connected by {addr}")

        while True:
            # Receive a message from the administrator
            message = conn.recv(1024).decode('utf-8')

            if not message:
                break

            print(f"Admin Message: {message}")

            # Broadcast the message to all connected clients (you need to implement this part)
            # You can maintain a list of connected clients and send the message to each of them
            # using their individual sockets.
