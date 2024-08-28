import asyncio
from slixmpp import ClientXMPP
from slixmpp.exceptions import IqError, IqTimeout
import sys
import threading
import xml.etree.ElementTree as ET

# Forzar el uso de SelectorEventLoop en Windows
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

class XMPPClient(ClientXMPP):
    def __init__(self, jid, password, auth_callback):
        # Constructor de la clase XMPPClient. Se inicializa con JID, contraseña y un callback para autenticación.
        super().__init__(jid=jid, password=password)
        self.auth_callback = auth_callback
        self.authenticated = False
        self.contact_jid = None  # Para almacenar el JID del contacto que se desea agregar
        self.contacts_callback = None  # Callback para manejar la lista de contactos
        self.jid = jid  # Guardar el JID del usuario para excluirlo de la lista de contactos
        self.detail_callback = None  # Callback para manejar los detalles de un contacto
        self.set_handlers()  # Configurar los manejadores de eventos

    def set_handlers(self):
        # Asignar manejadores de eventos específicos para diferentes situaciones
        self.add_event_handler("session_start", self.start)  # Evento al iniciar sesión
        self.add_event_handler("failed_auth", self.failed_auth)  # Evento en caso de fallo de autenticación
        self.add_event_handler("presence_subscribed", self.on_subscribed)  # Evento cuando se confirma la suscripción
        self.add_event_handler("presence_subscribe", self.on_subscribe)  # Evento al recibir una solicitud de suscripción

    async def start(self, event):
        # Método que se ejecuta al iniciar sesión
        print("Conexión exitosa: Autenticado con el servidor XMPP.")
        self.send_presence(pshow="chat", pstatus="Connected")  # Enviar presencia como conectado
        await self.get_roster()  # Obtener la lista de contactos
        self.authenticated = True
        self.auth_callback(True)  # Ejecutar el callback de autenticación exitosa

        # Si hay un contacto para agregar, enviar la solicitud de suscripción
        if self.contact_jid:
            await self.add_contact(self.contact_jid)

        # Obtener y devolver todos los contactos después de la autenticación
        if self.contacts_callback:
            contacts = self.get_all_contacts()
            self.contacts_callback(contacts)

    def get_all_contacts(self):
        """Devuelve una lista con todos los contactos del usuario, excluyendo el propio JID."""
        contacts = []
        for jid in self.client_roster.keys():
            if jid != self.jid:  # Excluir el propio JID
                contacts.append(jid)
        return contacts

    def get_contact_details(self, contact_jid):
        """Devuelve el estado de presencia de un contacto específico."""
        presence = self.client_roster.presence(contact_jid)
        if presence:
            for resource, pres in presence.items():
                show = pres.get('show', 'chat')  # Obtener el estado de presencia, por defecto 'chat'
                return show  # Devuelve el primer estado de presencia encontrado
        return "Desconocido"

    def failed_auth(self, event):
        # Método que se ejecuta cuando falla la autenticación
        print("Fallo en la autenticación: No se pudo autenticar con el servidor XMPP.")
        self.authenticated = False
        self.auth_callback(False)  # Ejecutar el callback de fallo de autenticación
        self.disconnect()  # Desconectar del servidor

    async def add_contact(self, contact_jid):
        """Envío de solicitud de suscripción."""
        self.send_presence_subscription(pto=contact_jid)
        print(f"Solicitud de suscripción enviada a {contact_jid}")
        
        # Actualizar la lista de contactos en tiempo real
        await self.get_roster()
        if self.contacts_callback:
            contacts = self.get_all_contacts()
            self.contacts_callback(contacts)

    def on_subscribed(self, presence):
        """Confirmación de la suscripción."""
        print(f"Ahora estás suscrito a {presence['from'].bare}")

    def on_subscribe(self, presence):
        """Responder a las solicitudes de suscripción entrantes."""
        self.send_presence_subscription(pto=presence['from'].bare)
        print(f"Solicitud de suscripción de {presence['from'].bare} aceptada")

    async def delete_my_account(self):
        """
        Eliminar la cuenta del usuario del servidor enviando una IQ con una solicitud de 'remove'.
        """
        try:
            # Crear una nueva IQ (consulta)
            iq = self.make_iq_set()

            # Construir manualmente el elemento 'query' con la solicitud de 'remove'
            query = ET.Element('{jabber:iq:register}query')
            remove = ET.SubElement(query, 'remove')

            # Adjuntar el elemento 'query' al IQ
            iq.append(query)

            # Enviar la IQ y esperar la respuesta
            result = await iq.send()

            print("SUCCESS: Cuenta eliminada exitosamente del servidor")
            return True

        except IqError as e:
            print(f"ERROR: Fallo al eliminar la cuenta: {e.iq['error']['text']}")
            return False
        except IqTimeout:
            print("ERROR: Timeout mientras se intentaba eliminar la cuenta")
            return False

    async def create_account(self):
        """
        Crear una nueva cuenta en el servidor enviando una IQ con los detalles de registro.
        """
        try:
            iq = self.make_iq_set()
            query = ET.Element('{jabber:iq:register}query')
            username = ET.SubElement(query, 'username')
            password = ET.SubElement(query, 'password')
            username.text = self.boundjid.user
            password.text = self.password
            iq.append(query)

            await iq.send()
            print("SUCCESS: Cuenta creada exitosamente")
            return True
        except IqError as e:
            print(f"ERROR: Fallo al crear la cuenta: {e.iq['error']['text']}")
            return False
        except IqTimeout:
            print("ERROR: Timeout mientras se intentaba crear la cuenta")
            return False

# Función para iniciar el cliente XMPP en un hilo separado
def start_xmpp(jid, password, auth_callback, contacts_callback=None):
    def run_xmpp():
        loop = asyncio.new_event_loop()  # Crear un nuevo bucle de eventos
        asyncio.set_event_loop(loop)  # Establecer este bucle como el bucle de eventos del hilo actual

        xmpp = XMPPClient(jid, password, auth_callback)
        xmpp.contacts_callback = contacts_callback  # Asignar el callback de contactos
        xmpp.connect(disable_starttls=True, use_ssl=False)
        
        loop.run_until_complete(xmpp.process(forever=False))  # Ejecutar el bucle de eventos hasta que se complete el proceso

    thread = threading.Thread(target=run_xmpp)
    thread.start()

# Función para agregar un contacto a través de un hilo separado
def add_contact(jid, password, contact_jid, auth_callback):
    def run_xmpp_with_contact():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        xmpp = XMPPClient(jid, password, auth_callback)
        xmpp.contact_jid = contact_jid  # Asignar el JID del contacto a agregar
        xmpp.connect(disable_starttls=True, use_ssl=False)
        
        loop.run_until_complete(xmpp.process(forever=False))

    thread = threading.Thread(target=run_xmpp_with_contact)
    thread.start()

# Función para obtener detalles de un contacto específico
def get_contact_details(jid, password, contact_jid, detail_callback):
    def run_xmpp_for_details():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        xmpp = XMPPClient(jid, password, lambda x: None)
        xmpp.connect(disable_starttls=True, use_ssl=False)

        async def process_details():
            await xmpp.get_roster()
            detail = xmpp.get_contact_details(contact_jid)
            detail_callback(contact_jid, detail)
            xmpp.disconnect()

        loop.run_until_complete(process_details())

    thread = threading.Thread(target=run_xmpp_for_details)
    thread.start()

# Función para eliminar una cuenta XMPP
def delete_xmpp_account(jid, password, callback):
    def run_xmpp_delete():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        xmpp = XMPPClient(jid, password, lambda x: None)
        xmpp.connect(disable_starttls=True, use_ssl=False)

        async def delete_and_disconnect():
            success = await xmpp.delete_my_account()
            xmpp.disconnect()
            callback(success)

        loop.run_until_complete(delete_and_disconnect())

    thread = threading.Thread(target=run_xmpp_delete)
    thread.start()

# Función para crear una cuenta XMPP
def create_xmpp_account(jid, password, callback):
    def run_xmpp_create():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        xmpp = XMPPClient(jid, password, lambda x: None)
        xmpp.connect(disable_starttls=True, use_ssl=False)

        async def create_and_disconnect():
            success = await xmpp.create_account()
            xmpp.disconnect()
            callback(success)

        loop.run_until_complete(create_and_disconnect())

    thread = threading.Thread(target=run_xmpp_create)
    thread.start()
