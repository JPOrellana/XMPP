import tkinter as tk
from tkinter import messagebox
from connection.conn import connect_to_server
import asyncio

import sys
import os

# Agregar la ruta absoluta al sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'connection')))

from conn import connect_to_server




class LoginGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Iniciar Sesión")
        self.root.geometry("400x300")
        self.root.configure(bg='gray')

        # Título
        self.title_label = tk.Label(self.root, text="Iniciar Sesión", font=("Helvetica", 16), bg='gray', fg='white')
        self.title_label.pack(pady=20)

        # Usuario
        self.user_label = tk.Label(self.root, text="Usuario", font=("Helvetica", 12), bg='gray', fg='white')
        self.user_label.pack(pady=5)
        self.user_entry = tk.Entry(self.root, width=30)
        self.user_entry.pack(pady=5)

        # Contraseña
        self.password_label = tk.Label(self.root, text="Contraseña", font=("Helvetica", 12), bg='gray', fg='white')
        self.password_label.pack(pady=5)
        self.password_entry = tk.Entry(self.root, show='*', width=30)
        self.password_entry.pack(pady=5)

        # Botón de Ingresar
        self.login_button = tk.Button(self.root, text="Ingresar", command=self.login, width=15)
        self.login_button.pack(pady=20)

    def login(self):
        username = self.user_entry.get()
        password = self.password_entry.get()

        try:
            xmpp = connect_to_server(username, password)
            self.root.after(2000, self.validate_login, xmpp)
        except Exception as e:
            self.show_message("Credenciales incorrectas. No se puede conectar", error=True)

    def validate_login(self, xmpp):
        if xmpp.authenticated:
            self.show_message("Ingresó Correctamente", error=False)
            self.root.after(2000, self.open_chat, xmpp)
        else:
            self.show_message("Credenciales incorrectas. No se puede conectar", error=True)
            xmpp.disconnect()

    def show_message(self, message, error=False):
        if error:
            messagebox.showerror("Error", message)
        else:
            messagebox.showinfo("Éxito", message)

    def open_chat(self, xmpp):
        self.root.destroy()  # Cierra la ventana de login
        import principal
        principal.run_chat(xmpp)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    login_gui = LoginGUI()
    login_gui.run()
