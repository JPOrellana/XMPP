from flask import Flask, render_template, request, jsonify, redirect, url_for
import asyncio
import slixmpp
import sys

# Forzar el uso de SelectorEventLoop en Windows
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

app = Flask(__name__)

class TestClient(slixmpp.ClientXMPP):
    def __init__(self, jid, password):
        super().__init__(jid, password)
        self.add_event_handler("session_start", self.start)
        self.add_event_handler("message", self.message_handler)
        self.add_event_handler("failed_auth", self.failed_auth)
        self.register_plugin('xep_0030')  # Service Discovery
        self.register_plugin('xep_0199')  # XMPP Ping
        self.auth_failed = False

    async def start(self, event):
        self.send_presence()
        await self.get_roster()
        print("Conexión exitosa y sesión iniciada.")
        self.disconnect()

    def message_handler(self, msg):
        if msg['type'] in ('chat', 'normal'):
            print(f"Mensaje recibido de {msg['from']}: {msg['body']}")

    def failed_auth(self, event):
        print("Autenticación fallida.")
        self.auth_failed = True
        self.disconnect()

def run_xmpp_client(jid, password):
    xmpp = TestClient(jid, password)
    xmpp.connect(disable_starttls=True, use_ssl=False)
    xmpp.process(forever=False)
    return not xmpp.auth_failed

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/connect', methods=['POST'])
def connect():
    data = request.json
    jid = data['jid']
    password = data['password']

    # Ejecutar el cliente XMPP en un nuevo hilo de eventos
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    success = run_xmpp_client(jid, password)

    if success:
        # Redirigir a la página principal si la conexión es exitosa
        return jsonify({"status": "Conectado"}), 200
    else:
        # Devolver un error si la autenticación falla
        return jsonify({"status": "Error"}), 401

@app.route('/principal')
def principal():
    return render_template('principal.html')

if __name__ == '__main__':
    app.run(debug=True)
