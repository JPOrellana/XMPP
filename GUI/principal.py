import asyncio
import tkinter as tk
from tkinter import scrolledtext

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from connection.conn import EchoBot  

class ChatGUI:
    def __init__(self, xmpp):
        self.xmpp = xmpp

        self.root = tk.Tk()
        self.root.title("XMPP Chat")

        self.text_area = scrolledtext.ScrolledText(self.root, wrap=tk.WORD)
        self.text_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        self.text_area.config(state=tk.DISABLED)

        self.entry = tk.Entry(self.root)
        self.entry.pack(padx=10, pady=(0, 10), fill=tk.X)

        self.send_button = tk.Button(self.root, text="Send", command=self.send_message)
        self.send_button.pack(pady=(0, 10))

    def send_message(self):
        message = self.entry.get()
        if message:
            self.entry.delete(0, tk.END)
            asyncio.create_task(self.xmpp.handle_send_message(message))

    def display_message(self, message):
        self.text_area.config(state=tk.NORMAL)
        self.text_area.insert(tk.END, message + "\n")
        self.text_area.config(state=tk.DISABLED)
        self.text_area.see(tk.END)

    def run(self):
        self.root.mainloop()


if __name__ == '__main__':
    gui = ChatGUI(None)
    xmpp = EchoBot('ore21970-test1@alumchat.lol', 'pruebas', gui)
    gui.xmpp = xmpp

    xmpp.connect(disable_starttls=True, use_ssl=False)
    asyncio.create_task(xmpp.process(forever=True))

    gui.run()
