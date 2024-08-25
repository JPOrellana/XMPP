import slixmpp
import asyncio

class ChatClient(slixmpp.ClientXMPP):
    def __init__(self, jid, password):
        super().__init__(jid, password)
        self.add_event_handler("session_start", self.start)
        self.add_event_handler("message", self.message)

    async def start(self, event):
        self.send_presence()
        await self.get_roster()

    def message(self, msg):
        # Lógica para recibir mensajes
        if msg['type'] in ('chat', 'normal'):
            print(f"Mensaje recibido de {msg['from']}: {msg['body']}")
            # Aquí puedes agregar la lógica para mostrar el mensaje en la interfaz

    def send_message_to(self, mto, message):
        # Lógica para enviar mensajes
        self.send_message(mto=mto, mbody=message, mtype='chat')
        print("Mensaje enviado.")

def iniciarNuevoChat(jid, password, recipient):
    xmpp = ChatClient(jid, password)
    xmpp.connect(disable_starttls=True, use_ssl=False)
    xmpp.process(forever=False)

    # Enviar un mensaje inicial
    xmpp.send_message_to(recipient, "Hola, iniciemos el chat!")
