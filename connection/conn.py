import asyncio
from slixmpp import ClientXMPP

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
            await asyncio.sleep(0.001)  # Keep the event loop running
            self.gui.root.update()  # Call update() on the root window

    def message(self, msg):
        if msg["type"] in ("chat", "normal"):
            sender = str(msg["from"]).split("/")[0]  # Eliminar la parte del recurso
            body = msg["body"]
            formatted_message = f"{sender.split('@')[0]}\n{body}"  # Formatear el mensaje

            if sender == self.jid.split("/")[0]:  # Si soy yo, enviar como "Yo"
                self.gui.display_message(formatted_message, sender="Yo")
            else:
                self.gui.display_message(formatted_message, sender=sender)

    async def handle_send_message(self, message, target_user):
        self.send_msg(mto=target_user, mbody=message)
        username = self.jid.split('@')[0]
        formatted_message = f"{username}\n{message}"
        self.gui.display_message(formatted_message, sender="Yo")  # Mostrar el mensaje en la GUI

    def send_msg(self, mto: str, mbody: str):
        self.send_message(mto=mto, mbody=mbody)

def start_xmpp(gui):
    xmpp = EchoBot('ore21970-te@alumchat.lol', 'pruebas', gui)
    gui.xmpp = xmpp

    xmpp.connect(disable_starttls=True, use_ssl=False)
    asyncio.create_task(xmpp.process(forever=True))
