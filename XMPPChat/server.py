from flask import Flask, render_template, request, jsonify, redirect, url_for
import asyncio
import sys
from prueba import send_message

# Forzar el uso de SelectorEventLoop en Windows
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

app = Flask(__name__)

current_jid = None
current_password = None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/connect', methods=['POST'])
def connect():
    global current_jid, current_password
    data = request.json
    jid = data['jid']
    password = data['password']

    current_jid = jid
    current_password = password

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        loop.run_until_complete(send_message(jid, password, None, None))
        return redirect(url_for('principal'))
    except Exception as e:
        print(f"Error al conectar: {e}")
        return jsonify({"status": "Error"}), 500

@app.route('/send_message', methods=['POST'])
def send_message_route():
    global current_jid, current_password
    data = request.json
    recipient = data['recipient']
    message = data['message']

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        loop.run_until_complete(send_message(current_jid, current_password, recipient, message))
        return jsonify({"status": "Mensaje enviado"}), 200
    except Exception as e:
        print(f"Error al enviar mensaje: {e}")
        return jsonify({"status": "Error"}), 500

@app.route('/principal')
def principal():
    return render_template('principal.html')

if __name__ == '__main__':
    app.run(debug=True)
