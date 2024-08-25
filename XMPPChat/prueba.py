import slixmpp
import asyncio
import sys

# Forzar el uso de SelectorEventLoop en Windows
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

class XMPPClient(slixmpp.ClientXMPP):
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

    def message(self, msg):
        if msg['type'] in ('chat', 'normal'):
            print(f"Mensaje recibido de {msg['from']}: {msg['body']}")

    def send_xmpp_message(self, recipient, message):
        self.send_message(mto=recipient, mbody=message, mtype='chat')
        print(f"Mensaje enviado a {recipient}: {message}")

async def send_message(jid, password, recipient, message):
    try:
        xmpp = XMPPClient(jid, password)
        connection = await xmpp.connect(disable_starttls=True, use_ssl=False)
        
        if connection is None:
            raise RuntimeError("Failed to establish connection to XMPP server.")
        
        xmpp.process(forever=False)
        
        if recipient and message:
            xmpp.send_xmpp_message(recipient, message)
        
        xmpp.disconnect()
    
    except Exception as e:
        print(f"Error al conectar: {e}")
