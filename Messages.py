from quiz import rooms
from Room import Room

def _get_room(room_number):
    if room_number in rooms:
        room = rooms[room_number]
    else:
        room = Room()
    return room


def handle_message(message, room_number, ws):
    message_type = message['type']
    room_number = int(message['room'])
    room = _get_room(room_number)

    if message_type == 'start':
        room.add_player(ws)

        if room_number not in rooms:
            rooms[room_number] = room

    elif message_type == 'answer':
        room
        

def handle_disconnect(room_number, ws):
    room = rooms[room_number]
    if room.players_count() == 1:
        del rooms[room_number]
    else:
        room.remove_player(ws)