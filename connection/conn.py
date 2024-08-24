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

    async def handle_send_message(self, message):
        self.send_msg(mto='lei21752-test@alumchat.lol', mbody=message)
        username = self.jid.split('@')[0]
        self.gui.display_message(f"{username}\n{message}")  # Mostrar el mensaje en la GUI

    def message(self, message):
        if message["type"] == "chat":
            emitter = str(message["from"])
            actual_name = emitter.split("/")[0]
            message_body = message["body"]
            print(f"Mensaje recibido de {actual_name}: {message_body}")  # Línea de depuración
            self.gui.display_message(f"[{actual_name}]\n{message_body}")


    def send_msg(self, mto: str, mbody: str):
        self.send_message(mto, mbody)

def start_xmpp(gui):
    xmpp = EchoBot('ore21970-te@alumchat.lol', 'pruebas', gui)
    gui.xmpp = xmpp

    xmpp.connect(disable_starttls=True, use_ssl=False)
    asyncio.create_task(xmpp.process(forever=True))