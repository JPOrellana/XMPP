import sys
import asyncio
from slixmpp import ClientXMPP
import base64
from typing import Optional

# Forzar el uso de SelectorEventLoop en Windows
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

class XMPPClient(ClientXMPP):
    def __init__(self, jid, password):
        super().__init__(jid=jid, password=password)
        self.recv_msg = None
        self.set_handlers()
        self._register_plugins()
        print("done")

    def _register_plugins(self):
        self.register_plugin('xep_0030')  # Service Discovery
        self.register_plugin('xep_0065')  # SOCKS5 Bytestreams
        self.register_plugin('xep_0095')  # Stream Initiation
        self.register_plugin('xep_0096')  # SI File Transfer
        self.register_plugin('xep_0004')  # Data Forms

    async def start(self, event):
        self.send_presence(pshow="chat", pstatus="Connected")
        await self.get_roster()

    def set_recv_msg(self, recv_msg: callable):
        self.recv_msg = recv_msg

    def send_msg(self, mto, msg):
        self.send_message(mto=mto, mbody=msg, mtype='chat')

    async def receive_message(self, message):
        if message["type"] == "chat":
            emitter = str(message["from"])
            actual_name = emitter.split("/")[0]
            message_body = message["body"]

            if message_body.startswith("file://"):
                file_content = message["body"].split("://")
                file_name = file_content[1]
                file_data = file_content[2]
                decoded_file_data = base64.b64decode(file_data)
                file_to_write = open(f"../files_recv/{file_name}", "wb")
                file_to_write.write(decoded_file_data)
                msg_data = {
                    "emitter": actual_name,
                    "body": f"A file was sent by {actual_name}!"
                }
            else:
                msg_data = {
                    "emitter": actual_name,
                    "body": message_body
                }

            if self.recv_msg:
                self.recv_msg(msg_data)
            else:
                print(f"{actual_name}: {message_body}")

    def failed_auth(self):
        print("Failed to Authenticate")
        self.disconnect()

    def set_handlers(self):
        self.add_event_handler("message", self.receive_message)
        self.add_event_handler("failed_auth", self.failed_auth)
        self.add_event_handler("session_start", self.start)

def send_messages(xmpp, destinatario):
    while True:
        mensaje = input("Qué mensaje vas a enviar: ")
        if mensaje.lower() == "salir":
            print("Terminando el chat...")
            xmpp.disconnect(wait=True)
            break
        xmpp.send_msg(destinatario, mensaje)
        print(f"Mensaje enviado a {destinatario}: {mensaje}")

def main():
    xmpp = XMPPClient("ore21970-te@alumchat.lol", "pruebas")
    xmpp.connect(disable_starttls=True, use_ssl=False)

    # Ejecutar el procesamiento de mensajes de XMPP directamente en el loop principal
    loop = asyncio.get_event_loop()
    
    # Procesar mensajes de XMPP sin bloquear el loop principal
    loop.create_task(xmpp.process(forever=True))

    destinatario = "bau21889-test@alumchat.lol"
    send_messages(xmpp, destinatario)

if __name__ == "__main__":
    main()
