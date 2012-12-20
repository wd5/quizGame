from flask import Flask, render_template, request
from geventwebsocket.handler import WebSocketHandler
from gevent.pywsgi import WSGIServer
import simplejson
import Messages

app = Flask(__name__)

rooms = {}

@app.route('/')
def index():
    return render_template('index.html', rooms_keys=rooms.keys())

@app.route('/room/<int:room>')
def room(room):
    return render_template('room.html', room_number=room)

@app.route('/roomWS')
def rooms_ws():
    if 'wsgi.websocket' in request.environ:
        ws = request.environ['wsgi.websocket']
        room_number = None

        while True:
            message = ws.receive()

            if message is None:
                Messages.handle_disconnect(room_number, ws)
                break
            else:
                message = simplejson.loads(message)
                Messages.handle_message(message, ws)

    return

if __name__ == '__main__':
    http_server = WSGIServer(('', 5000), app, handler_class=WebSocketHandler)
    http_server.serve_forever()