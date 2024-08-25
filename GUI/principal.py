import tkinter as tk
from tkinter import scrolledtext, Menu, messagebox
import asyncio
import sys
import os

# Añadir la ruta para importar conn
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from connection.conn import start_xmpp  # Importamos la función que inicia la conexión

class ChatGUI:
    def __init__(self):
        self.xmpp = None  # La conexión XMPP se asignará después
        self.chats = {}  # Diccionario para almacenar los chats y sus mensajes
        self.target_user = None  # Variable para almacenar el usuario objetivo

        self.root = tk.Tk()
        self.root.title("XMPP Chat")
        self.root.geometry("900x700")  # Tamaño de la ventana
        self.root.configure(bg='#e5e5e5')  # Fondo blanco para una apariencia limpia

        # Crear el menú principal
        menubar = Menu(self.root)
        self.root.config(menu=menubar)

        # Crear el menú "Menú"
        menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Menú", menu=menu)

        # Añadir opciones al menú
        menu.add_command(label="Nuevo Chat", command=self.new_chat)
        menu.add_command(label="Chat Grupal", command=self.new_group_chat)
        menu.add_command(label="Detalle Contacto", command=self.contact_detail)
        menu.add_command(label="Agregar Contacto", command=self.add_contact)
        menu.add_command(label="Mostrar Todos los Contactos", command=self.show_all_contacts)

        # Frame principal
        self.main_frame = tk.Frame(self.root, bg='#e5e5e5')
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Frame izquierdo para mostrar todos los chats
        self.chat_list_frame = tk.Frame(self.main_frame, bg='#f0f0f0', width=200)
        self.chat_list_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        self.chat_list_label = tk.Label(self.chat_list_frame, text="Chats", font=("Helvetica", 14), bg='#f0f0f0')
        self.chat_list_label.pack(pady=10)

        # Listbox para mostrar los chats
        self.chat_listbox = tk.Listbox(self.chat_list_frame, font=("Helvetica", 12))
        self.chat_listbox.pack(fill=tk.BOTH, expand=True)
        self.chat_listbox.bind('<<ListboxSelect>>', self.load_chat)

        # Área de texto donde se muestran los mensajes
        self.text_area = scrolledtext.ScrolledText(self.main_frame, wrap=tk.WORD, state=tk.DISABLED, font=("Helvetica", 10))
        self.text_area.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Configuración de estilos para los mensajes
        self.text_area.tag_configure("username_send", foreground="blue", font=("Helvetica", 10, "bold"))
        self.text_area.tag_configure("username_receive", foreground="red", font=("Helvetica", 10, "bold"))
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

    def clear_chat(self):
        """Limpia el área de texto del chat"""
        self.text_area.config(state=tk.NORMAL)
        self.text_area.delete('1.0', tk.END)
        self.text_area.config(state=tk.DISABLED)

    def new_chat(self):
        """Maneja la creación de un nuevo chat abriendo una ventana emergente personalizada"""
        # Crear la ventana emergente
        popup = tk.Toplevel(self.root)
        popup.title("Nuevo Chat")
        popup.geometry("400x200")  # Tamaño de la ventana emergente
        popup.configure(bg='#e5e5e5')

        # Etiqueta
        label = tk.Label(popup, text="Ingrese Usuario:", font=("Helvetica", 12), bg='#e5e5e5')
        label.pack(pady=20)

        # Entrada de texto
        entry = tk.Entry(popup, font=("Helvetica", 12))
        entry.pack(pady=5, padx=20, fill=tk.X)

        # Botón para iniciar chat
        def on_confirm():
            self.target_user = entry.get()
            if self.target_user:
                if self.target_user in self.chats:
                    messagebox.showinfo("Chat Existente", "Ya existe un chat con este usuario.")
                else:
                    self.chats[self.target_user] = []  # Crear un nuevo chat si no existe
                    self.chat_listbox.insert(tk.END, self.target_user)  # Añadir el chat a la lista de chats con el dominio completo
                    self.root.title(f"Chateando con {self.target_user}")
                popup.destroy()
                self.load_chat()  # Cargar el chat recién creado o seleccionado

        button = tk.Button(popup, text="Iniciar", bg='#0078D7', fg='white', font=("Helvetica", 10), relief="flat", command=on_confirm)
        button.pack(pady=5)

    def new_group_chat(self):
        """Maneja la creación de un nuevo chat grupal"""
        self.clear_chat()  # Limpiar el área de chat cuando se inicia un nuevo chat grupal
        # Aquí se puede añadir la lógica para manejar chats grupales en el futuro.

    def contact_detail(self):
        """Muestra detalles del contacto"""
        # Lógica para detalle de contacto
        pass

    def add_contact(self):
        """Añadir un nuevo contacto"""
        # Lógica para agregar contacto
        pass

    def show_all_contacts(self):
        """Mostrar todos los contactos"""
        # Lógica para mostrar todos los contactos
        pass

    def load_chat(self, event=None):
        """Carga los mensajes del chat seleccionado en el área de mensajes"""
        selection = self.chat_listbox.curselection()
        if selection:
            selected_chat = self.chat_listbox.get(selection[0])
            self.target_user = self.get_full_user(selected_chat)  # Recuperar el usuario completo
            self.clear_chat()  # Limpiar el área de chat antes de mostrar los mensajes
            if self.target_user in self.chats:  # Asegurarse de que el chat existe
                for message in self.chats[self.target_user]:
                    self.display_message(message, sender=self.target_user)

    def get_full_user(self, display_name):
        """Recupera el nombre de usuario completo basado en el nombre mostrado"""
        for user in self.chats:
            if display_name == user:
                return user
        return display_name  # Si no se encuentra, devuelve el nombre mostrado tal cual

    def send_message(self):
        message = self.entry.get("1.0", tk.END).strip()
        if message and self.xmpp and self.target_user:
            formatted_message = f"Yo\n{message}"
            if self.target_user not in self.chats:
                self.chats[self.target_user] = []  # Inicializar el chat si no existe
            self.chats[self.target_user].append(formatted_message)  # Guardar el mensaje en el chat
            self.entry.delete("1.0", tk.END)
            asyncio.create_task(self.xmpp.handle_send_message(message, self.target_user))
            self.display_message(formatted_message, sender="Yo")  # Mostrar el mensaje enviado en la GUI

    def display_message(self, message, sender):
        self.text_area.config(state=tk.NORMAL)
        if sender == "Yo":
            tag = "username_send"
        else:
            tag = "username_receive"
        username, msg = message.split('\n', 1)  # Dividimos el mensaje en nombre de usuario y contenido
        self.text_area.insert(tk.END, username + "\n", tag)  # Insertar nombre de usuario en el color correspondiente y en negrita
        self.text_area.insert(tk.END, msg + "\n", "message")  # Insertar mensaje en negro normal
        self.text_area.config(state=tk.DISABLED)
        self.text_area.see(tk.END)

    def run(self):
        start_xmpp(self)  # Iniciamos la conexión cuando la GUI se ejecuta
        self.root.mainloop()

if __name__ == '__main__':
    gui = ChatGUI()
    gui.run()
