# lan_chat_server.py
import socket
import threading
import ldap
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

class LANChatServer:
    def __init__(self, host, port, ldap_server, ldap_base_dn):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_sockets = {}
        self.noticeboard_messages = []
        self.ldap_server = ldap_server
        self.ldap_base_dn = ldap_base_dn
        self.ldap_conn = self.setup_ldap_connection()

    def setup_ldap_connection(self):
        ldap_conn = ldap.initialize(self.ldap_server)
        return ldap_conn

    def authenticate_user(self, username, password):
        try:
            user_dn = f"CN={username},{self.ldap_base_dn}"
            self.ldap_conn.simple_bind_s(user_dn, password)
            return True
        except ldap.INVALID_CREDENTIALS:
            return False

    def send_message(self, sender_username, message):
        encrypted_message = f"{sender_username}: {message}".encode()
        for client_socket in self.client_sockets.values():
            client_socket.send(encrypted_message)

    def send_general_notification(self, notification):
        for client_socket in self.client_sockets.values():
            client_socket.send(f"[Notification] {notification}".encode())

    def send_noticeboard_messages(self, client_socket):
        for notice in self.noticeboard_messages:
            client_socket.send(notice.encode())

    def handle_client(self, client_socket, client_type):
        # Perform domain authentication for desktop clients
        if client_type == "desktop":
            client_socket.send("Enter domain username:".encode())
            username = client_socket.recv(1024).decode()
            client_socket.send("Enter domain password:".encode())
            password = client_socket.recv(1024).decode()

            if self.authenticate_user(username, password):
                print(f"[*] New connection from {username}")
                # Notify the connected client about successful authentication
                client_socket.send("Authentication successful!".encode())
                # Store the client socket in the dictionary with the username as the key
                self.client_sockets[username] = client_socket
                # Send noticeboard messages to the connected client
                self.send_noticeboard_messages(client_socket)

                while True:
                    try:
                        message = client_socket.recv(1024).decode()
                        if not message:
                            break

                        # Check if it's an admin command
                        if message.startswith("/admin "):
                            self.handle_admin_command(message, username)
                        else:
                            print(f"[*] Message from {username}: {message}")
                            # Broadcast the message to all clients
                            self.send_message(username, message)

                    except socket.error:
                        print(f"[!] {username} disconnected.")
                        # Remove the disconnected client
                        del self.client_sockets[username]
                        break
            else:
                client_socket.send("Authentication failed. Disconnecting...".encode())
                client_socket.close()

        # For mobile clients, assume a simple authentication mechanism
        elif client_type == "mobile":
            # You may want to implement a more secure authentication method for mobile users
            # For simplicity, the code below assumes successful authentication for any connection
            print("[*] New mobile connection")
            client_socket.send("Authentication successful!".encode())
            while True:
                try:
                    message = client_socket.recv(1024).decode()
                    if not message:
                        break

                    # Handle mobile client messages
                    print("[*] Message from mobile client:", message)

                except socket.error:
                    print("[!] Mobile client disconnected.")
                    break

    def handle_admin_command(self, command, username):
        if username == "admin":
            command_parts = command.split(" ")
            if command_parts[1] == "notice":
                notice_message = " ".join(command_parts[2:])
                self.broadcast_notice(notice_message)
            elif command_parts[1] == "users":
                user_list = ", ".join(self.client_sockets.keys())
                self.send_message("admin", f"Connected Users: {user_list}")

    def broadcast_notice(self, notice_message):
        notice = f"[Notice] {notice_message}"
        self.noticeboard_messages.append(notice)
        self.send_message("admin", notice)
        self.send_general_notification(notice)

    def start_server(self):
        @app.route('/')
        def index():
            return render_template('index.html')

        @app.route('/send_message', methods=['POST'])
        def send_message():
            message = request.form['message']
            self.send_general_notification(message)
            return redirect(url_for('index'))

        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()

        print(f"[*] Server listening on {self.host}:{self.port}")

        while True:
            client_socket, _ = self.server_socket.accept()
            client_type = client_socket.recv(1024).decode()
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket, client_type))
            client_thread.start()

if __name__ == "__main__":
    # Replace the following with your LDAP server details
    ldap_server = "ldap://your-ldap-server"
    ldap_base_dn = "dc=your-domain,dc=com"

    # Use '0.0.0.0' to make the server accessible on all network interfaces
    server = LANChatServer("0.0.0.0", 12345, ldap_server, ldap_base_dn)
    server.start_server()
