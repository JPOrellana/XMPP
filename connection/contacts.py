import asyncio
from slixmpp import ClientXMPP

class AddContactBot(ClientXMPP):
    def __init__(self, jid, password, contact_jid):
        super().__init__(jid, password)
        self.contact_jid = contact_jid

        # Manejadores de eventos
        self.add_event_handler("session_start", self.start)
        self.add_event_handler("presence_subscribed", self.on_subscribed)
        self.add_event_handler("presence_subscribe", self.on_subscribe)

    async def start(self, event):
        """Envío de solicitud de suscripción."""
        self.send_presence()
        await self.get_roster()

        self.send_presence_subscription(pto=self.contact_jid)
        print(f"Solicitud de suscripción enviada a {self.contact_jid}")
        self.disconnect()

    def on_subscribed(self, presence):
        """Confirmación de la suscripción."""
        print(f"Ahora estás suscrito a {presence['from'].bare}")

    def on_subscribe(self, presence):
        """Responder a las solicitudes de suscripción entrantes."""
        self.send_presence_subscription(pto=presence['from'].bare)
        print(f"Solicitud de suscripción de {presence['from'].bare} aceptada")

def add_contact(jid, password, contact_jid):
    xmpp = AddContactBot(jid, password, contact_jid)
    xmpp.connect(disable_starttls=True, use_ssl=False)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(xmpp.process(forever=False))
