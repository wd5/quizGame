from flask import Flask, render_template, request, g
from geventwebsocket.handler import WebSocketHandler
from gevent.pywsgi import WSGIServer
import simplejson
import messages
import quiz_globals

app = Flask(__name__)

all_constants = [item for item in dir(quiz_globals) if not item.startswith('__')]
for constant in all_constants:
    app.jinja_env.globals[constant] = getattr(quiz_globals, constant)

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
        g.rooms = rooms
        room_number = None
        player_name = None

        while True:
            message = ws.receive()

            if message is None:
                messages.handle_disconnect(room_number, player_name)
                break
            else:
                message = simplejson.loads(message)
                room_number = int(message['room'])
                player_name = message['user']
                messages.handle_message(message, room_number, player_name, ws)

    return

if __name__ == '__main__':
    http_server = WSGIServer(('', 5000), app, handler_class=WebSocketHandler)
    http_server.serve_forever()