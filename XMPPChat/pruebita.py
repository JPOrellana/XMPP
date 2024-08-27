import sys
import asyncio
from slixmpp import ClientXMPP
import base64
from threading import Thread
from typing import Optional

# Forzar el uso de SelectorEventLoop en Windows
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

class XMPPClient(ClientXMPP):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(XMPPClient, cls).__new__(cls)
        return cls._instance

    def __init__(self, jid, password):
        if not hasattr(self, '_initialized'):
            super().__init__(jid=jid, password=password)
            self._initialized = True
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
        try:
            print(f"Enviando mensaje a {mto}: {msg}")
            self.send_message(mto=mto, mbody=msg, mtype='chat')
            print(f"Mensaje enviado a {mto}: {msg}")
        except Exception as e:
            print(f"Error al enviar mensaje: {e}")

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
                print(f"Mensaje recibido de {actual_name}: {message_body}")

    def add_contact(self, jid: str, name: Optional[str] = None):
        self.send_presence_subscription(pto=jid)
        if name:
            self.update_roster(jid, name=name)

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

def main():
    # Ingresar usuario, contraseña y destinatario desde la consola
    jid = input("Ingresa tu JID (usuario@dominio): ")
    password = input("Ingresa tu contraseña: ")
    destinatario = input("Ingresa el JID del destinatario: ")

    xmpp = XMPPClient(jid, password)
    xmpp.connect(disable_starttls=True, use_ssl=False)
    
    # Iniciar el procesamiento de mensajes en un hilo separado
    xmpp_thread = Thread(target=xmpp.process, kwargs={"forever": True})
    xmpp_thread.start()

    send_messages(xmpp, destinatario)

    # Esperar a que el procesamiento termine antes de salir
    xmpp_thread.join()

if __name__ == "__main__":
    main()
