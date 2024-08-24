import tkinter as tk
from tkinter import scrolledtext
import asyncio
import sys
import os

# Añadir la ruta para importar conn
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from connection.conn import start_xmpp  # Importamos la función que inicia la conexión

class ChatGUI:
    def __init__(self):
        self.xmpp = None  # La conexión XMPP se asignará después

        self.root = tk.Tk()
        self.root.title("XMPP Chat")
        self.root.geometry("900x700")  # Tamaño de la ventana
        self.root.configure(bg='#e5e5e5')  # Fondo blanco para una apariencia limpia

        # Frame principal
        self.main_frame = tk.Frame(self.root, bg='#e5e5e5')
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Frame izquierdo para los botones y las opciones de contacto
        self.left_frame = tk.Frame(self.main_frame, bg='#f0f0f0', width=200)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        # Botones Nuevo Chat y Chat Grupal
        self.chat_buttons_frame = tk.Frame(self.left_frame, bg='#f0f0f0')
        self.chat_buttons_frame.pack(pady=10)

        self.new_chat_button = tk.Button(self.chat_buttons_frame, text="Nuevo Chat", bg='#0078D7', fg='white', font=("Helvetica", 10), relief="flat", width=12)
        self.new_chat_button.pack(side=tk.LEFT, padx=(0, 5))

        self.group_chat_button = tk.Button(self.chat_buttons_frame, text="Chat Grupal", bg='#0078D7', fg='white', font=("Helvetica", 10), relief="flat", width=12)
        self.group_chat_button.pack(side=tk.LEFT)

        # Contenedor de Detalle de Contacto
        self.contact_detail_frame = tk.Frame(self.left_frame, bg='#f0f0f0')
        self.contact_detail_frame.pack(fill=tk.X, pady=(20, 10))

        self.contact_detail_label = tk.Label(self.contact_detail_frame, text="Detalle Contacto", font=("Helvetica", 12), bg='#f0f0f0')
        self.contact_detail_label.pack(pady=(0, 5))

        self.contact_detail_entry = tk.Entry(self.contact_detail_frame, font=("Helvetica", 10))
        self.contact_detail_entry.pack(fill=tk.X, padx=10, pady=5)

        self.contact_detail_button = tk.Button(self.contact_detail_frame, text="Buscar", bg='#0078D7', fg='white', font=("Helvetica", 10), relief="flat")
        self.contact_detail_button.pack(pady=10)

        # Contenedor de Agregar Contacto
        self.add_contact_frame = tk.Frame(self.left_frame, bg='#f0f0f0')
        self.add_contact_frame.pack(fill=tk.X, pady=(20, 10))

        self.add_contact_label = tk.Label(self.add_contact_frame, text="Agregar Contacto", font=("Helvetica", 12), bg='#f0f0f0')
        self.add_contact_label.pack(pady=(0, 5))

        self.add_contact_entry = tk.Entry(self.add_contact_frame, font=("Helvetica", 10))
        self.add_contact_entry.pack(fill=tk.X, padx=10, pady=5)

        self.add_contact_button = tk.Button(self.add_contact_frame, text="Agregar", bg='#0078D7', fg='white', font=("Helvetica", 10), relief="flat")
        self.add_contact_button.pack(pady=10)

        # Contenedor de Todos los Contactos
        self.all_contacts_frame = tk.Frame(self.left_frame, bg='#f0f0f0')
        self.all_contacts_frame.pack(fill=tk.X, pady=(20, 10))

        self.all_contacts_button = tk.Button(self.all_contacts_frame, text="Todos los contactos", bg='#0078D7', fg='white', font=("Helvetica", 10), relief="flat")
        self.all_contacts_button.pack(pady=10)

        # Área de texto donde se muestran los mensajes
        self.text_area = scrolledtext.ScrolledText(self.main_frame, wrap=tk.WORD, state=tk.DISABLED, font=("Helvetica", 10))
        self.text_area.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Configuración de estilos para los mensajes
        self.text_area.tag_configure("username", foreground="blue", font=("Helvetica", 10, "bold"))
        self.text_area.tag_configure("message", foreground="black", font=("Helvetica", 10))

        # Frame para la entrada de texto y el botón de envío
        self.entry_frame = tk.Frame(self.root, bg='#e5e5e5')
        self.entry_frame.pack(fill=tk.X, padx=10, pady=10)

        # Entrada de texto donde el usuario escribe el mensaje
        self.entry = tk.Text(self.entry_frame, height=2, wrap=tk.WORD, font=("Helvetica", 10))
        self.entry.pack(side=tk.LEFT, padx=(0, 10), fill=tk.X, expand=True)

        # Botón de envío al lado derecho del cuadro de entrada de texto
        self.send_button = tk.Button(self.entry_frame, text="Enviar", command=self.send_message, width=10, bg='#0078D7', fg='white', font=("Helvetica", 10), relief="flat")
        self.send_button.pack(side=tk.RIGHT)

    def send_message(self):
        message = self.entry.get("1.0", tk.END).strip()
        if message and self.xmpp:
            self.entry.delete("1.0", tk.END)
            asyncio.create_task(self.xmpp.handle_send_message(message))

    def display_message(self, message):
        self.text_area.config(state=tk.NORMAL)
        username, msg = message.split('\n', 1)  # Dividimos el mensaje en nombre de usuario y contenido
        self.text_area.insert(tk.END, username + "\n", "username")  # Insertar nombre de usuario en azul y negrita
        self.text_area.insert(tk.END, msg + "\n", "message")  # Insertar mensaje en negro normal
        self.text_area.config(state=tk.DISABLED)
        self.text_area.see(tk.END)

    def run(self):
        start_xmpp(self)  # Iniciamos la conexión cuando la GUI se ejecuta
        self.root.mainloop()

if __name__ == '__main__':
    gui = ChatGUI()
    gui.run()
