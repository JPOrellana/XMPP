from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_socketio import SocketIO, emit
import asyncio
import slixmpp
import sys

# Forzar el uso de SelectorEventLoop en Windows
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app)

class TestClient(slixmpp.ClientXMPP):
    def __init__(self, jid, password):
        super().__init__(jid, password)
        self.add_event_handler("session_start", self.start)
        self.add_event_handler("message", self.message_handler)
        self.add_event_handler("failed_auth", self.failed_auth)
        self.register_plugin('xep_0030')  # Service Discovery
        self.register_plugin('xep_0199')  # XMPP Ping
        self.auth_failed = False
        self.destinatario = None  # Variable para almacenar el destinatario actual

    async def start(self, event):
        self.send_presence()
        await self.get_roster()
        print("Conexión exitosa y sesión iniciada.")
        # Aquí recuperamos y mostramos la lista de contactos
        roster = self.client_roster
        contacts = [jid for jid in roster]
        # Emitir la lista de contactos al cliente a través de WebSockets
        socketio.emit('update_contacts', {'contacts': contacts})

    def message_handler(self, msg):
        if msg['type'] in ('chat', 'normal'):
            print(f"Mensaje recibido de {msg['from']}: {msg['body']}")
            # Aquí podrías añadir lógica para enviar el mensaje recibido a la interfaz

    def failed_auth(self, event):
        print("Autenticación fallida.")
        self.auth_failed = True
        self.disconnect()

    def set_destinatario(self, destinatario):
        self.destinatario = destinatario

    def send_message_to_destinatario(self, message):
        if self.destinatario:
            self.send_message(mto=self.destinatario, mbody=message, mtype='chat')
            print(f"Mensaje enviado a {self.destinatario}: {message}")

    def add_contact(self, contact_jid):
        self.send_presence_subscription(pto=contact_jid)
        print(f"Solicitud de suscripción enviada a {contact_jid}")
        # Notificar al cliente de la adición del nuevo contacto
        socketio.emit('new_contact', {'contact_jid': contact_jid})

def run_xmpp_client(jid, password):
    xmpp = TestClient(jid, password)
    xmpp.connect(disable_starttls=True, use_ssl=False)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(xmpp.start(None))  # Llamamos al método start de forma manual
    return xmpp

# Mantendremos el cliente XMPP globalmente para enviar mensajes desde cualquier parte de la app
xmpp_client = None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/connect', methods=['POST'])
def connect():
    global xmpp_client
    data = request.json
    jid = data['jid']
    password = data['password']

    # Ejecutar el cliente XMPP en un nuevo hilo de eventos
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    xmpp_client = run_xmpp_client(jid, password)

    if not xmpp_client.auth_failed:
        # Redirigir a la página principal si la conexión es exitosa
        return jsonify({"status": "Conectado"}), 200
    else:
        # Devolver un error si la autenticación falla
        return jsonify({"status": "Error"}), 401

@app.route('/principal')
def principal():
    return render_template('principal.html')

@app.route('/iniciar_chat', methods=['POST'])
def iniciar_chat():
    global xmpp_client
    data = request.json
    usuario = data['usuario']
    
    if xmpp_client:
        xmpp_client.set_destinatario(usuario)
        return jsonify({"status": "Chat iniciado con " + usuario})
    else:
        return jsonify({"status": "Error", "message": "Cliente XMPP no conectado"}), 400

@app.route('/send_message', methods=['POST'])
def send_message():
    global xmpp_client
    data = request.json
    message = data['message']
    
    if xmpp_client:
        xmpp_client.send_message_to_destinatario(message)
        return jsonify({"status": "Mensaje enviado"})
    else:
        return jsonify({"status": "Error", "message": "Cliente XMPP no conectado"}), 400

@app.route('/add_contact', methods=['POST'])
def add_contact():
    global xmpp_client
    data = request.json
    contact_jid = data['contact_jid']
    
    if xmpp_client:
        xmpp_client.add_contact(contact_jid)
        return jsonify({"status": "Contacto agregado"})
    else:
        return jsonify({"status": "Error", "message": "Cliente XMPP no conectado"}), 400

@app.route('/logout', methods=['POST'])
def logout():
    global xmpp_client
    
    if xmpp_client:
        xmpp_client.disconnect(wait=True)  # Desconectar el XMPP
        xmpp_client = None  # Eliminar la instancia global
    
    return jsonify({"status": "Sesión cerrada"}), 200

if __name__ == '__main__':
    socketio.run(app, debug=True)
