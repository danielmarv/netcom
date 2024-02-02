import socket
import tkinter as tk
from tkinter import ttk, messagebox
from plyer import notification
import sqlite3

class UserClient:
    def __init__(self, server_host, server_port):
        self.server_host = server_host
        self.server_port = server_port
        self.root = tk.Tk()

        # Set up Tkinter UI
        self.root.title("User Dashboard")
        self.style = ttk.Style(self.root)
        self.style.theme_use("clam")

        self.message_label = ttk.Label(self.root, text="User Dashboard", font=('Helvetica', 16, 'bold'))
        self.message_label.pack(pady=10)

        self.messages_text = tk.Text(self.root, height=10, width=40, font=('Helvetica', 12))
        self.messages_text.pack(pady=10, padx=20)
        self.messages_text.configure(state='disabled')

        # Start a separate thread to continuously receive messages
        import threading
        threading.Thread(target=self.receive_messages, daemon=True).start()

    def receive_messages(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((self.server_host, self.server_port))

            while True:
                message = client_socket.recv(1024).decode('utf-8')
                if not message:
                    break

                # Display the message in the Tkinter Text widget
                self.messages_text.configure(state='normal')
                self.messages_text.insert(tk.END, message + '\n')
                self.messages_text.see(tk.END)
                self.messages_text.configure(state='disabled')

                # Show notification
                notification.notify(
                    title='New Message',
                    message=message,
                    timeout=5
                )

if __name__ == '__main__':
    user_client = UserClient('172.24.0.1', 5555)
    user_client.root.mainloop()
