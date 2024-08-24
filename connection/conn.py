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
        self.authenticated = True  # Indicamos que la autenticación fue exitosa
        if self.gui:
            asyncio.create_task(self.gui_update_loop())

    async def gui_update_loop(self):
        while True:
            await asyncio.sleep(0.001)  # Mantener el bucle de eventos en ejecución
            self.gui.root.update()  # Actualizar la GUI

    async def handle_send_message(self, message):
        self.send_msg(mto='ore21970-te@alumchat.lol', mbody=message)

    def message(self, message):
        if message["type"] == "chat":
            emitter = str(message["from"])
            actual_name = emitter.split("/")[0]
            message_body = message["body"]
            if self.gui:
                self.gui.display_message(f"from: {actual_name}\n{message_body}")

    def send_msg(self, mto: str, mbody: str):
        self.send_message(mto, mbody)

def start_xmpp(jid, password, gui=None):
    xmpp = EchoBot(jid, password, gui)
    xmpp.connect(disable_starttls=True, use_ssl=False)
    return xmpp