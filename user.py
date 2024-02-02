import socket
import tkinter as tk
from tkinter import messagebox

class UserClient:
    def __init__(self, server_host, server_port):
        self.server_host = server_host
        self.server_port = server_port

        self.root = tk.Tk()

        # Set up Tkinter UI
        self.root.title("User Client")
        self.message_label = tk.Label(self.root, text="Received Messages:")
        self.message_label.pack(pady=10)
        self.message_text = tk.Text(self.root, height=10, width=40)
        self.message_text.pack()

        # Start a separate thread to continuously receive messages
        import threading
        threading.Thread(target=self.receive_messages, daemon=True).start()

    def receive_messages(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((self.server_host, self.server_port))

            while True:
                # Receive and display messages
                message = client_socket.recv(1024).decode('utf-8')
                if not message:
                    break

                # Display the message in the Tkinter Text widget
                self.message_text.insert(tk.END, message + '\n')
                self.message_text.see(tk.END)

if __name__ == '__main__':
    user_client = UserClient('your_server_ip', 5555)
    user_client.root.mainloop()
