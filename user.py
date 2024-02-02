import socket
import tkinter as tk
from tkinter import ttk, messagebox

class UserClient:
    def __init__(self, server_host, server_port):
        self.server_host = server_host
        self.server_port = server_port

        self.root = tk.Tk()

        # Set up Tkinter UI
        self.root.title("User Client")
        self.style = ttk.Style(self.root)
        self.style.theme_use("clam")  # You can try different themes like "scidblue", "vista", etc.

        self.message_label = ttk.Label(self.root, text="Received Messages:", font=('Helvetica', 12, 'bold'))
        self.message_label.pack(pady=10)

        self.message_text = tk.Text(self.root, height=10, width=40, font=('Helvetica', 12))
        self.message_text.pack(pady=10, padx=20)
        self.message_text.configure(state='disabled')  # Disable text widget for read-only

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
                self.message_text.configure(state='normal')  # Enable text widget for writing
                self.message_text.insert(tk.END, message + '\n')
                self.message_text.see(tk.END)
                self.message_text.configure(state='disabled')  # Disable text widget for read-only

if __name__ == '__main__':
    user_client = UserClient('172.24.0.1', 5555)
    user_client.root.mainloop()

