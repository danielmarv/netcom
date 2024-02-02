import socket
import tkinter as tk
from tkinter import ttk, simpledialog

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

        # Start a separate thread for the server
        import threading
        threading.Thread(target=self.start_server, daemon=True).start()

    def broadcast_message(self, message):
        for client in self.clients:
            try:
                client.sendall(message.encode('utf-8'))
            except Exception as e:
                print(f"Error broadcasting message to client: {e}")

    def start_server(self):
        while True:
            conn, addr = self.server_socket.accept()
            self.clients.append(conn)
            print(f"Connected by {addr}")

class AdminUI:
    def __init__(self, admin_server):
        self.admin_server = admin_server
        self.root = tk.Tk()

        # Set up Tkinter UI
        self.root.title("Admin UI")
        self.style = ttk.Style(self.root)
        self.style.theme_use("clam")  # You can try different themes like "scidblue", "vista", etc.

        self.message_entry = ttk.Entry(self.root, font=('Helvetica', 12))
        self.message_entry.pack(pady=10, padx=20, ipady=5, fill='x')

        self.send_button = ttk.Button(self.root, text="Send Message", command=self.send_message)
        self.send_button.pack(pady=10, padx=20, ipady=5, fill='x')

    def send_message(self):
        message = self.message_entry.get()
        self.admin_server.broadcast_message(message)
        self.message_entry.delete(0, tk.END)
        tk.messagebox.showinfo("Message Sent", "Message sent to all clients.")

    def run(self):
        self.root.mainloop()

if __name__ == '__main__':
    admin_server = AdminServer('0.0.0.0', 5555)
    admin_ui = AdminUI(admin_server)
    admin_ui.run()
