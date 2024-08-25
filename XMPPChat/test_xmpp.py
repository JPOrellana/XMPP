import slixmpp
import asyncio
import sys

# Forzar el uso de SelectorEventLoop en Windows
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

class TestClient(slixmpp.ClientXMPP):
    def __init__(self, jid, password):
        super().__init__(jid, password)
        self.add_event_handler("session_start", self.start)
        self.add_event_handler("message", self.message)
        self.register_plugin('xep_0030')  # Service Discovery
        self.register_plugin('xep_0199')  # XMPP Ping

    async def start(self, event):
        self.send_presence()
        await self.get_roster()
        print("Conexión exitosa y sesión iniciada.")
        self.send_message(mto="bau21889-test@alumchat.lol", mbody="Hola, he conectado exitosamente!", mtype='chat')
        print("Mensaje enviado.")
        self.disconnect()

    def message(self, msg):
        if msg['type'] in ('chat', 'normal'):
            print(f"Mensaje recibido de {msg['from']}: {msg['body']}")

jid = "ore21970-te@alumchat.lol"
password = "pruebas"

xmpp = TestClient(jid, password)
xmpp.connect(disable_starttls=True, use_ssl=False)
xmpp.process(forever=False)
