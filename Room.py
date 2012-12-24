import threading
import simplejson
import quiz_globals

def _get_simple_json_message(message):
    return simplejson.dumps(dict(type=message))

class Room():
    def __init__(self):
        self._players = []
        self._question_timer = None


    def add_player(self, player):
        self._players.append(player)

        if self.players_count() == 1:
            self.start_quiz()


    def players_count(self):
        return len(self._players)


    def remove_player(self, player):
        self._players.remove(player)


    def _send_all_players(self, data):
        for player in self._players:
            player.send(data)


    def _send_all_players_except_one(self, except_player, data):
        for player in self._players:
            if player != except_player:
                player.send(data)


    def start_quiz(self):
        question_data = simplejson.dumps(dict(type = quiz_globals.QUESTION_MESSAGE_TO_CLIENT, topic='some topic', question='some question'))
        self._send_all_players(question_data)
        self._question_timer = threading.Timer(12, self.show_answer)
        self._question_timer.start()


    def show_answer(self):
        self._send_all_players(simplejson.dumps(dict(type=quiz_globals.ANSWER_MESSAGE_TO_CLIENT, answer='answer')))

        if self.players_count():
            self._question_timer = threading.Timer(5, self.start_quiz)
            self._question_timer.start()


    def handle_player_answer(self, player, is_correct):
        pass


    def wait_answer(self, player):
        self._question_timer.cancel()
        self._send_all_players_except_one(player, _get_simple_json_message(quiz_globals.STOP_ANSWER_MESSAGE_TO_CLIENT))