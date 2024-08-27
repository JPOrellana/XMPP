import tkinter as tk
from tkinter import scrolledtext, Menu, messagebox
import sys
import os
import asyncio

# Añadir la ruta para importar conn
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from connection.conn import start_xmpp, add_contact, get_contact_details, delete_xmpp_account  # Importamos las funciones necesarias

class ChatGUI:
    def __init__(self):
        self.xmpp = None  # La conexión XMPP se asignará después
        self.jid = None  # Almacena el JID del usuario que inició sesión
        self.password = None  # Almacena la contraseña del usuario que inició sesión
        self.chats = {}  # Diccionario para almacenar los chats y sus mensajes
        self.target_user = None  # Variable para almacenar el usuario objetivo
        self.contacts = []  # Almacena la lista de contactos

        self.root = tk.Tk()
        self.root.title("XMPP Chat")
        self.root.geometry("900x700")  # Tamaño de la ventana
        self.root.configure(bg='#e5e5e5')  # Fondo blanco para una apariencia limpia

        # Crear el menú principal en la barra de tareas
        self.menubar = Menu(self.root)
        self.root.config(menu=self.menubar)

        # Añadir la opción "Iniciar Sesión" a la barra de tareas
        self.menubar.add_command(label="Iniciar Sesión", command=self.show_login_screen)

        # Añadir la opción "Cerrar Sesión" a la barra de tareas, inicialmente deshabilitada
        self.menubar.add_command(label="Cerrar Sesión", command=self.logout, state=tk.DISABLED)

        # Añadir la opción "Eliminar Cuenta" a la barra de tareas, deshabilitada al inicio
        self.menubar.add_command(label="Eliminar Cuenta", command=self.delete_account_gui, state=tk.DISABLED)

        # Crear el menú "Menú" en la barra de tareas
        self.menu = Menu(self.menubar, tearoff=0)
        self.menu.add_command(label="Chat Grupal", command=self.new_group_chat, state=tk.DISABLED)
        self.menu.add_command(label="Detalle Contacto", command=self.contact_detail, state=tk.DISABLED)
        self.menu.add_command(label="Agregar Contacto", command=self.add_contact_gui, state=tk.DISABLED)
        self.menubar.add_cascade(label="Menú", menu=self.menu, state=tk.DISABLED)  # Inicialmente deshabilitado

        # Frame principal para contenido dinámico
        self.main_frame = tk.Frame(self.root, bg='#e5e5e5')
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Mostrar la pantalla de inicio de sesión al iniciar
        self.show_login_screen()

    def show_login_screen(self):
        """Mostrar pantalla de inicio de sesión en la misma ventana principal."""
        # Limpiar la pantalla principal
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        # Deshabilitar el menú durante el inicio de sesión
        self.menubar.entryconfig("Menú", state=tk.DISABLED)
        self.menubar.entryconfig("Cerrar Sesión", state=tk.DISABLED)
        self.menubar.entryconfig("Eliminar Cuenta", state=tk.DISABLED)  # Deshabilitar la opción 'Eliminar Cuenta'

        # Etiqueta y entradas para JID y contraseña
        tk.Label(self.main_frame, text="JID:", font=("Helvetica", 12), bg='#e5e5e5').pack(pady=10)
        self.jid_entry = tk.Entry(self.main_frame, font=("Helvetica", 12))
        self.jid_entry.pack(pady=5, padx=20, fill=tk.X)

        tk.Label(self.main_frame, text="Contraseña:", font=("Helvetica", 12), bg='#e5e5e5').pack(pady=10)
        self.password_entry = tk.Entry(self.main_frame, font=("Helvetica", 12), show="*")
        self.password_entry.pack(pady=5, padx=20, fill=tk.X)

        self.login_button = tk.Button(self.main_frame, text="Iniciar Sesión", bg='#0078D7', fg='white', font=("Helvetica", 10), relief="flat", command=self.on_login)
        self.login_button.pack(pady=20)

    def on_login(self):
        jid = self.jid_entry.get()
        password = self.password_entry.get()
        if jid and password:
            self.jid = jid  # Almacenar el JID del usuario autenticado
            self.password = password  # Almacenar la contraseña del usuario autenticado
            # Deshabilitar el botón mientras se espera la autenticación
            self.login_button.config(state=tk.DISABLED)
            self.root.after(100, self.try_login(jid, password))

    def try_login(self, jid, password):
        # Ejecutar el procesamiento de mensajes de XMPP directamente en el loop principal
        start_xmpp(jid, password, self.handle_auth_result, self.load_contacts)

    def handle_auth_result(self, success):
        if success:
            self.auth_successful()
        else:
            self.auth_failed()

    def auth_successful(self):
        """Acciones que se toman después de una autenticación exitosa."""
        messagebox.showinfo("Conexión Exitosa", "Conectado con éxito al servidor.")
        self.enable_menu()
        self.show_chat_interface()

    def auth_failed(self):
        """Acciones que se toman después de una autenticación fallida."""
        messagebox.showerror("Error de Conexión", "No se logró conectar al servidor.")
        self.login_button.config(state=tk.NORMAL)  # Rehabilitar el botón si falla

    def enable_menu(self):
        """Habilitar el menú y deshabilitar 'Iniciar Sesión'."""
        self.menubar.entryconfig("Menú", state=tk.NORMAL)
        self.menubar.entryconfig("Iniciar Sesión", state=tk.DISABLED)
        self.menubar.entryconfig("Cerrar Sesión", state=tk.NORMAL)  # Desbloquear 'Cerrar Sesión'
        self.menubar.entryconfig("Eliminar Cuenta", state=tk.NORMAL)  # Habilitar 'Eliminar Cuenta'

        # Habilitar opciones de chat en el menú
        self.menu.entryconfig("Chat Grupal", state=tk.NORMAL)
        self.menu.entryconfig("Detalle Contacto", state=tk.NORMAL)
        self.menu.entryconfig("Agregar Contacto", state=tk.NORMAL)

    def show_chat_interface(self):
        """Mostrar la interfaz de chat después de un inicio de sesión exitoso."""
        # Limpiar la pantalla principal
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        # Frame izquierdo para mostrar todos los chats
        self.chat_list_frame = tk.Frame(self.main_frame, bg='#f0f0f0', width=200)
        self.chat_list_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        self.chat_list_label = tk.Label(self.chat_list_frame, text="Chats", font=("Helvetica", 14), bg='#f0f0f0')
        self.chat_list_label.pack(pady=10)

        # Listbox para mostrar los chats
        self.chat_listbox = tk.Listbox(self.chat_list_frame, font=("Helvetica", 12))
        self.chat_listbox.pack(fill=tk.BOTH, expand=True)
        self.chat_listbox.bind('<<ListboxSelect>>', self.load_chat)

        # Frame derecho que contiene el área de mensajes y la entrada
        self.right_frame = tk.Frame(self.main_frame, bg='#e5e5e5')
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Área de texto donde se muestran los mensajes
        self.text_area = scrolledtext.ScrolledText(self.right_frame, wrap=tk.WORD, state=tk.DISABLED, font=("Helvetica", 10))
        self.text_area.pack(fill=tk.BOTH, expand=True)

        # Frame para la entrada de texto y el botón de envío, ubicado en la parte inferior
        self.entry_frame = tk.Frame(self.right_frame, bg='#e5e5e5')
        self.entry_frame.pack(fill=tk.X, pady=(10, 0))

        # Entrada de texto donde el usuario escribe el mensaje
        self.entry = tk.Text(self.entry_frame, height=2, wrap=tk.WORD, font=("Helvetica", 10))
        self.entry.pack(side=tk.LEFT, padx=(0, 10), fill=tk.X, expand=True)

        # Botón de envío al lado derecho del cuadro de entrada de texto
        self.send_button = tk.Button(self.entry_frame, text="Enviar", command=self.send_message, width=10, bg='#0078D7', fg='white', font=("Helvetica", 10), relief="flat")
        self.send_button.pack(side=tk.RIGHT)

    def delete_account_gui(self):
        """GUI para eliminar la cuenta logueada"""
        popup = tk.Toplevel(self.root)
        popup.title("Eliminar Cuenta")
        popup.geometry("300x200")
        popup.configure(bg='#e5e5e5')

        tk.Label(popup, text="¿Seguro que desea eliminar la cuenta?", font=("Helvetica", 12), bg='#e5e5e5').pack(pady=20)

        def on_delete():
            confirm = messagebox.askyesno("Confirmación", "Esta acción es irreversible. ¿Desea continuar?")
            if confirm:
                delete_xmpp_account(self.jid, self.password, self.delete_account_callback)
                popup.destroy()

        tk.Button(popup, text="Eliminar", command=on_delete, bg='#D9534F', fg='white', font=("Helvetica", 10)).pack(pady=20)

    def delete_account_callback(self, success):
        """Callback después de intentar eliminar una cuenta"""
        if success:
            messagebox.showinfo("Cuenta Eliminada", "La cuenta ha sido eliminada con éxito.")
            self.logout()
        else:
            messagebox.showerror("Error", "No se pudo eliminar la cuenta.")

    def clear_chat(self):
        """Limpia el área de texto del chat"""
        self.text_area.config(state=tk.NORMAL)
        self.text_area.delete('1.0', tk.END)
        self.text_area.config(state=tk.DISABLED)

    def new_group_chat(self):
        """Maneja la creación de un nuevo chat grupal"""
        self.clear_chat()  # Limpiar el área de chat cuando se inicia un nuevo chat grupal
        # Aquí se puede añadir la lógica para manejar chats grupales en el futuro.

    def contact_detail(self):
        """Muestra detalles del contacto al ingresar un JID."""
        popup = tk.Toplevel(self.root)
        popup.title("Detalle Contacto")
        popup.geometry("300x200")
        popup.configure(bg='#e5e5e5')

        tk.Label(popup, text="Ingrese JID del contacto:", font=("Helvetica", 12), bg='#e5e5e5').pack(pady=10)
        jid_entry = tk.Entry(popup, font=("Helvetica", 12))
        jid_entry.pack(pady=5, padx=20, fill=tk.X)

        def on_consult():
            contact_jid = jid_entry.get().strip()
            if contact_jid:
                get_contact_details(self.jid, self.password, contact_jid, self.show_contact_details)
                popup.destroy()
            else:
                messagebox.showerror("Error", "El JID no puede estar vacío.")

        tk.Button(popup, text="Consultar", command=on_consult, bg='#0078D7', fg='white', font=("Helvetica", 10)).pack(pady=20)

    def show_contact_details(self, contact_jid, presence_status):
        """Muestra una ventana emergente con el detalle del contacto."""
        popup = tk.Toplevel(self.root)
        popup.title("Detalle del Contacto")
        popup.geometry("300x150")
        popup.configure(bg='#e5e5e5')

        status_map = {
            "chat": "Disponible",
            "away": "Ausente",
            "xa": "No Disponible",
            "dnd": "Ocupado"
        }

        status_text = status_map.get(presence_status, "Desconocido")

        tk.Label(popup, text=f"JID: {contact_jid}", font=("Helvetica", 12), bg='#e5e5e5').pack(pady=10)
        tk.Label(popup, text=f"Estado: {status_text}", font=("Helvetica", 12), bg='#e5e5e5').pack(pady=10)


    def add_contact_gui(self):
        """Añadir un nuevo contacto desde la GUI"""
        # Crear una ventana emergente para ingresar el JID del contacto
        popup = tk.Toplevel(self.root)
        popup.title("Agregar Contacto")
        popup.geometry("300x200")
        popup.configure(bg='#e5e5e5')

        tk.Label(popup, text="Ingrese JID del contacto:", font=("Helvetica", 12), bg='#e5e5e5').pack(pady=10)
        jid_entry = tk.Entry(popup, font=("Helvetica", 12))
        jid_entry.pack(pady=5, padx=20, fill=tk.X)

        def on_add():
            contact_jid = jid_entry.get().strip()
            if contact_jid:
                # Utilizar las credenciales almacenadas para agregar el contacto
                add_contact(self.jid, self.password, contact_jid, self.update_contacts)
                popup.destroy()
            else:
                messagebox.showerror("Error", "El JID no puede estar vacío.")

        tk.Button(popup, text="Agregar", command=on_add, bg='#0078D7', fg='white', font=("Helvetica", 10)).pack(pady=20)

    def update_contacts(self, success):
        if success:
            self.clear_contacts()
            start_xmpp(self.jid, self.password, self.handle_auth_result, self.load_contacts)

    def clear_contacts(self):
        """Limpiar la lista de contactos en la GUI"""
        self.chat_listbox.delete(0, tk.END)

    def load_contacts(self, contacts):
        """Cargar contactos en la lista de la interfaz."""
        self.contacts = contacts
        for contact in self.contacts:
            self.chat_listbox.insert(tk.END, contact)

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

            # Ejecutar la tarea asincrónica en el bucle de eventos de asyncio
            asyncio.run_coroutine_threadsafe(self.xmpp.handle_send_message(message, self.target_user), self.xmpp.loop)
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

    def logout(self):
        """Desconectar del servidor XMPP y volver al login."""
        if self.xmpp:
            # Intentar desconectar inmediatamente
            self.xmpp.disconnect(wait=True)  # 'wait=True' asegura que se espera a que se complete la desconexión
            self.xmpp = None

        # Limpiar la pantalla y volver al login
        self.show_login_screen()

        # Deshabilitar el menú y la opción 'Cerrar Sesión' de nuevo
        self.menubar.entryconfig("Menú", state=tk.DISABLED)
        self.menubar.entryconfig("Cerrar Sesión", state=tk.DISABLED)
        self.menubar.entryconfig("Iniciar Sesión", state=tk.NORMAL)
        self.menubar.entryconfig("Eliminar Cuenta", state=tk.DISABLED)  # Deshabilitar la opción 'Eliminar Cuenta'

        print("Desconectado del servidor XMPP y de vuelta al login.")


    def run(self):
        self.root.mainloop()

if __name__ == '__main__':
    gui = ChatGUI()
    gui.run()