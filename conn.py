import asyncio
import logging
import aioconsole
import tkinter as tk
from tkinter import scrolledtext

from slixmpp import ClientXMPP
from slixmpp.xmlstream import JID

# Allow async code to execute on Windows.
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

class EchoBot(ClientXMPP):

    def __init__(self, jid, password, gui):
        ClientXMPP.__init__(self, jid, password)
        self.gui = gui

        self.add_event_handler("session_start", self.session_start)
        self.add_event_handler("message", self.message)

    def session_start(self, event):
        self.send_presence()
        self.get_roster()
        asyncio.create_task(self.gui_update_loop())

    async def gui_update_loop(self):
        while True:
            await asyncio.sleep(0.01)  # Keep the event loop running
            self.gui.root.update()  # Call update() on the root window

    async def handle_send_message(self, message):
        self.send_msg(mto='ore21970-test1@alumchat.lol', mbody=message)

    def message(self, message):
        if message["type"] == "chat":
            emitter = str(message["from"])

            actual_name = emitter.split("/")[0]
            message_body = message["body"]
            self.gui.display_message(f"from: {actual_name}\n{message_body}")

    def send_msg(self, mto: str, mbody: str):
        self.send_message(mto, mbody)


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
    xmpp = EchoBot('ore21970-test1@alumchat.lol', 'pruebas', None)
    gui = ChatGUI(xmpp)
    xmpp.gui = gui

    xmpp.connect(disable_starttls=True, use_ssl=False)
    asyncio.create_task(xmpp.process(forever=True))

    gui.run()