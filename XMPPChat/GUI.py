import tkinter as tk
from tkinter import ttk, messagebox
from threading import Thread
from pruebita import XMPPClient

class ChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("XMPP Chat")
        self.xmpp = None

        # Crear un Notebook (pestañas)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=1, fill="both")

        # Pestaña de inicio de sesión
        self.login_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.login_frame, text="Iniciar Sesión")

        ttk.Label(self.login_frame, text="Usuario (JID):").grid(row=0, column=0, padx=10, pady=10)
        self.jid_entry = ttk.Entry(self.login_frame)
        self.jid_entry.grid(row=0, column=1, padx=10, pady=10)

        ttk.Label(self.login_frame, text="Contraseña:").grid(row=1, column=0, padx=10, pady=10)
        self.password_entry = ttk.Entry(self.login_frame, show="*")
        self.password_entry.grid(row=1, column=1, padx=10, pady=10)

        ttk.Label(self.login_frame, text="Destinatario (JID):").grid(row=2, column=0, padx=10, pady=10)
        self.recipient_entry = ttk.Entry(self.login_frame)
        self.recipient_entry.grid(row=2, column=1, padx=10, pady=10)

        self.login_button = ttk.Button(self.login_frame, text="Iniciar Sesión", command=self.login)
        self.login_button.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

        # Pestaña de chat
        self.chat_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.chat_frame, text="Chat")
        self.notebook.tab(1, state="disabled")

        self.messages_text = tk.Text(self.chat_frame, state="disabled", wrap="word")
        self.messages_text.pack(expand=1, fill="both", padx=10, pady=10)

        self.message_entry = ttk.Entry(self.chat_frame)
        self.message_entry.pack(side="left", fill="x", expand=1, padx=10, pady=10)

        self.send_button = ttk.Button(self.chat_frame, text="Enviar", command=self.send_message)
        self.send_button.pack(side="right", padx=10, pady=10)

    def login(self):
        jid = self.jid_entry.get()
        password = self.password_entry.get()
        recipient = self.recipient_entry.get()

        if not jid or not password or not recipient:
            messagebox.showerror("Error", "Todos los campos son obligatorios")
            return

        self.xmpp = XMPPClient(jid, password)
        self.xmpp.connect(disable_starttls=True, use_ssl=False)
        
        # Hilo para manejar la conexión y recepción de mensajes
        xmpp_thread = Thread(target=self.xmpp.process, kwargs={"forever": False})
        xmpp_thread.start()

        self.notebook.tab(1, state="normal")  # Habilitar la pestaña de chat
        self.notebook.select(1)  # Cambiar a la pestaña de chat

        # Redefinir la función para recibir mensajes y mostrarlos en la GUI
        self.xmpp.set_recv_msg(self.display_message)

    def send_message(self):
        message = self.message_entry.get()
        if message and self.recipient_entry.get():
            self.xmpp.send_msg(self.recipient_entry.get(), message)
            self.display_message({"emitter": "Yo", "body": message})
            self.message_entry.delete(0, tk.END)
            print(f"Mensaje enviado desde GUI a {self.recipient_entry.get()}: {message}")  # Mensaje de depuración


    def display_message(self, msg_data):
        self.messages_text.config(state="normal")
        self.messages_text.insert(tk.END, f"{msg_data['emitter']}: {msg_data['body']}\n")
        self.messages_text.config(state="disabled")
        self.messages_text.see(tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatApp(root)
    root.mainloop()
