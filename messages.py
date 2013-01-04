from quiz import rooms
from room import Room
import quiz_globals
import simplejson

def _get_room(room_number):
    if room_number in rooms:
        room = rooms[room_number]
    else:
        room = Room()
    return room


def handle_message(message, room_number, player_name, ws):
    message_type = message['type']
    room = _get_room(room_number)

    if message_type == quiz_globals.START_LISTENING_MESSAGE_TO_SERVER:
        room.add_player(player_name, ws)

        if room.players_count() == 1:
            room.start_quiz()

        if room_number not in rooms:
            rooms[room_number] = room

    elif message_type == quiz_globals.ANSWER_QUERY_MESSAGE_TO_SERVER:
        room.wait_answer(player_name)
    elif message_type == quiz_globals.PLAYER_ANSWER_MESSAGE_TO_SERVER:
        answer = message['answer']
        room.check_players_answer(player_name, answer)
        

def handle_disconnect(room_number, player_name):
    room = rooms[room_number]
    if room.players_count() == 1:
        del rooms[room_number]
    else:
        room.remove_player(player_name)