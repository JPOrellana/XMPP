import asyncio
from slixmpp import ClientXMPP
import base64

asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

class EchoBot(ClientXMPP):
    def __init__(self, jid, password, gui):
        ClientXMPP.__init__(self, jid, password)
        self.gui = gui

        self.add_event_handler("session_start", self.session_start)
        self.add_event_handler("message", self.receive_message)

    def session_start(self, event):
        self.send_presence()
        self.get_roster()
        asyncio.create_task(self.gui_update_loop())

    async def gui_update_loop(self):
        while True:
            await asyncio.sleep(0.001)  # Mantiene el loop de eventos de la GUI en ejecución
            self.gui.root.update()  # Llama a update() en la ventana raíz

    def receive_message(self, msg):
        """Maneja la recepción de mensajes y archivos"""
        if msg["type"] == "chat":
            emitter = str(msg["from"]).split("/")[0]  # Obtenemos el JID completo sin el recurso
            message_body = msg["body"]

            print(f"Mensaje recibido de: {emitter}")
            print(f"Usuario objetivo en GUI: {self.gui.target_user}")

            if message_body.startswith("file://"):
                # Manejo de archivo...
                pass
            else:
                formatted_message = f"{emitter}\n{message_body}"

            if emitter == self.gui.target_user:
                print("El mensaje será mostrado en la GUI.")
                self.gui.display_message(formatted_message, sender=emitter)
            else:
                print(f"Mensaje de otro usuario ignorado: {emitter}")


    async def handle_send_message(self, message, target_user):
        self.send_msg(mto=target_user, mbody=message)

    def send_msg(self, mto: str, mbody: str):
        self.send_message(mto=mto, mbody=mbody)

def start_xmpp(gui):
    xmpp = EchoBot('ore21970-te@alumchat.lol', 'pruebas', gui)
    gui.xmpp = xmpp

    xmpp.connect(disable_starttls=True, use_ssl=False)
    asyncio.create_task(xmpp.process(forever=True))
