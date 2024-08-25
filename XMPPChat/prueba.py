import sys
import asyncio
from slixmpp import ClientXMPP
import base64
from slixmpp.roster import RosterItem
from typing import Optional

# Forzar el uso de SelectorEventLoop en Windows
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

class XMPPClient(ClientXMPP):
    _instance = None

    # Implementación del patrón Singleton
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(XMPPClient, cls).__new__(cls)
        return cls._instance

    def __init__(self, jid, password):
        if not hasattr(self, '_initialized'):
            super().__init__(jid=jid, password=password)
            self._initialized = True
            self.recv_msg = None  # Inicializar recv_msg
            self.set_handlers()
            self._register_plugins()
            print("done")

    def _register_plugins(self):
        # Registrar plugins para transferencia de archivos
        self.register_plugin('xep_0030')  # Service Discovery
        self.register_plugin('xep_0065')  # SOCKS5 Bytestreams
        self.register_plugin('xep_0095')  # Stream Initiation
        self.register_plugin('xep_0096')  # SI File Transfer
        self.register_plugin('xep_0004')  # Data Forms

    async def start(self, event):
        self.send_presence(pshow="chat", pstatus="Connected")
        await self.get_roster()
        await asyncio.create_task(self.start_gui())

    async def start_gui(self):
        # Aquí puedes iniciar la interfaz gráfica si es necesario
        pass

    def set_recv_msg(self, recv_msg: callable):
        self.recv_msg = recv_msg

    def send_msg(self, mto, msg):
        self.send_message(mto=mto, mbody=msg, mtype='chat')

    async def send_file(self, mto, file_path):
        file_name = file_path.split("/")[-1]
        file = open(file_path, "rb")
        file_data = file.read()
        file_encoded_data = base64.b64encode(file_data).decode()
        await self.send_message(mto=mto, mbody=f"file://{file_name}://{file_encoded_data}", mtype="chat")

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

            # Verificar si recv_msg está configurado antes de llamarlo
            if self.recv_msg:
                self.recv_msg(msg_data)
            else:
                print(f"Mensaje recibido de {actual_name}: {message_body}")

    def get_contacts(self):
        contacts = []
        for jid in self.client_roster:
            contacts.append(jid)
        return contacts

    def add_contact(self, jid: str, name: Optional[str] = None):
        self.send_presence_subscription(pto=jid)
        if name:
            self.update_roster(jid, name=name)

    def get_contact_details(self, jid: str) -> Optional[RosterItem]:
        if jid in self.client_roster:
            return self.client_roster[jid]
        return None

    def failed_auth(self):
        print("Failed to Authenticate")
        self.disconnect()

    def set_handlers(self):
        self.add_event_handler("message", self.receive_message)
        self.add_event_handler("failed_auth", self.failed_auth)
        self.add_event_handler("session_start", self.start)

if __name__ == "__main__":
    xmpp = XMPPClient("ore21970-te@alumchat.lol", "pruebas")
    xmpp.connect(disable_starttls=True, use_ssl=False)
    xmpp.process(forever=False)
    xmpp.send_msg("bau21889-test@alumchat.lol", "¡Hola desde el cliente XMPP!")
