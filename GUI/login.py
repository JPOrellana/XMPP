import tkinter as tk
from tkinter import messagebox
import asyncio
import sys
import os

# Ajuste del path para importar conn.py
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from connection.conn import start_xmpp  # Importamos la función que inicia la conexión

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
        jid = self.user_entry.get()
        password = self.password_entry.get()

        try:
            xmpp = start_xmpp(jid, password, None)
            asyncio.create_task(xmpp.process(forever=False))

            # Validar la conexión de inmediato, sin esperar 2 segundos
            self.validate_login(xmpp)
        except Exception as e:
            self.show_message("Credenciales incorrectas. No se puede conectar", error=True)


    def validate_login(self, xmpp):
        if xmpp.authenticated:
            self.show_message("Ingresó Correctamente", error=False)
            asyncio.run(self.open_chat(xmpp))
        else:
            self.show_message("Credenciales incorrectas. No se puede conectar", error=True)
            xmpp.disconnect()


    def show_message(self, message, error=False):
        if error:
            messagebox.showerror("Error", message)
        else:
            messagebox.showinfo("Éxito", message)

    async def open_chat(self, xmpp):
        self.root.destroy()  # Cierra la ventana de login antes de abrir la nueva GUI
        import principal  # Importamos principal.py solo si la autenticación es correcta
        principal.run_chat(xmpp)

    def run(self):
        self.root.mainloop()
