import socket
import tkinter as tk
from tkinter import ttk, simpledialog, scrolledtext
import sqlite3
import threading

class AdminServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.clients = []

        # Set up the server socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()

        print(f"Admin Server listening on {self.host}:{self.port}")

        # Set up the SQLite database
        self.conn = sqlite3.connect('messages.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, message TEXT)')
        self.conn.commit()

        # Start a separate thread for the server
        import threading
        threading.Thread(target=self.start_server, daemon=True).start()

    def broadcast_message(self, message):
        for client in self.clients:
            try:
                client.sendall(message.encode('utf-8'))
            except Exception as e:
                print(f"Error broadcasting message to client: {e}")

    def save_message(self, message):
        self.cursor.execute('INSERT INTO messages (message) VALUES (?)', (message,))
        self.conn.commit()

    def get_messages(self):
        self.cursor.execute('SELECT message FROM messages')
        return self.cursor.fetchall()

    def start_server(self):
        while True:
            conn, addr = self.server_socket.accept()
            self.clients.append(conn)
            print(f"Connected by {addr}")

            # Send previous messages to the new client
            for msg in self.get_messages():
                conn.sendall(msg[0].encode('utf-8'))

            # Start a separate thread to handle messages for each client
            threading.Thread(target=self.handle_client, args=(conn,), daemon=True).start()

    def handle_client(self, client):
        while True:
            try:
                message = client.recv(1024).decode('utf-8')
                if not message:
                    break

                self.save_message(message)  # Save the message in the database
                self.broadcast_message(message)  # Broadcast the message to all clients
            except Exception as e:
                print(f"Error handling client: {e}")
                break

class AdminUI:
    def __init__(self, admin_server):
        self.admin_server = admin_server
        self.root = tk.Tk()

        # Set up Tkinter UI
        self.root.title("Admin Dashboard")
        self.style = ttk.Style(self.root)
        self.style.theme_use("clam")

        self.message_label = ttk.Label(self.root, text="Admin Dashboard", font=('Helvetica', 16, 'bold'))
        self.message_label.pack(pady=10)

        self.messages_text = scrolledtext.ScrolledText(self.root, height=10, width=40, font=('Helvetica', 12))
        self.messages_text.pack(pady=10, padx=20)
        self.messages_text.configure(state='disabled')

        # Start a separate thread to continuously update messages
        import threading
        threading.Thread(target=self.update_messages, daemon=True).start()

    def update_messages(self):
        while True:
            messages = '\n'.join([msg[0] for msg in self.admin_server.get_messages()])
            self.messages_text.configure(state='normal')
            self.messages_text.delete(1.0, tk.END)
            self.messages_text.insert(tk.END, messages)
            self.messages_text.see(tk.END)
            self.messages_text.configure(state='disabled')

    def run(self):
        self.root.mainloop()

if __name__ == '__main__':
    admin_server = AdminServer('0.0.0.0', 5555)
    admin_ui = AdminUI(admin_server)
    admin_ui.run()
