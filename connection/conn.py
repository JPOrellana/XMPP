import asyncio
from slixmpp import ClientXMPP
import sys
import threading

# Forzar el uso de SelectorEventLoop en Windows
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

class XMPPClient(ClientXMPP):
    def __init__(self, jid, password, auth_callback):
        super().__init__(jid=jid, password=password)
        self.auth_callback = auth_callback
        self.authenticated = False
        self.set_handlers()

    def set_handlers(self):
        self.add_event_handler("session_start", self.start)
        self.add_event_handler("failed_auth", self.failed_auth)

    async def start(self, event):
        print("Conexión exitosa: Autenticado con el servidor XMPP.")
        self.send_presence(pshow="chat", pstatus="Connected")
        await self.get_roster()
        self.authenticated = True
        self.auth_callback(True)

    def failed_auth(self, event):
        print("Fallo en la autenticación: No se pudo autenticar con el servidor XMPP.")
        self.authenticated = False
        self.auth_callback(False)
        self.disconnect()

def start_xmpp(jid, password, auth_callback):
    def run_xmpp():
        loop = asyncio.new_event_loop()  # Crear un nuevo bucle de eventos
        asyncio.set_event_loop(loop)  # Establecer este bucle como el bucle de eventos del hilo actual

        xmpp = XMPPClient(jid, password, auth_callback)
        xmpp.connect(disable_starttls=True, use_ssl=False)
        
        loop.run_until_complete(xmpp.process(forever=False))  # Ejecutar el bucle de eventos hasta que se complete el proceso

    thread = threading.Thread(target=run_xmpp)
    thread.start()
