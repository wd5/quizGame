import threading
import simplejson
import quiz_globals
import functools
from questions_cache import get_question_iter

def _get_simple_json_message(message):
    return simplejson.dumps(dict(type=message))

class Room():
    def __init__(self):
        self._players_sockets = {}
        self._players_scores = {}
        self._question_timer = None
        self._question = None
        self._question_iter = get_question_iter()


    def add_player(self, player_name, player_socket):
        self._players_sockets[player_name] = player_socket
        self._players_scores[player_name] = 0

        if self.players_count() == 1:
            self.start_quiz()


    def players_count(self):
        return len(self._players_sockets)


    def remove_player(self, player_name):
        del self._players_sockets[player_name]
        del self._players_scores[player_name]


    def _send_all_players(self, data):
        for player_socket in self._players_sockets.values():
            player_socket.send(data)


    def _send_all_players_except_one(self, except_player_name, data):
        for player_name in self._players_sockets:
            if player_name != except_player_name:
                self._players_sockets[player_name].send(data)


    def _change_player_score(self, player_name, delta_score):
        self._players_scores[player_name] += delta_score

        data = simplejson.dumps(dict(type=quiz_globals.SCORES_CHANGED_MESSAGE_TO_CLIENT, scores=self._players_scores))
        self._send_all_players(data)


    def start_quiz(self):
        self._question = next(self._question_iter)
        question_data = simplejson.dumps(
            dict(type = quiz_globals.QUESTION_MESSAGE_TO_CLIENT, topic=self._question[0], question=self._question[1]))
        self._send_all_players(question_data)
        self._question_timer = threading.Timer(12, self.show_answer)
        self._question_timer.start()


    def show_answer(self):
        self._send_all_players(simplejson.dumps(dict(type=quiz_globals.ANSWER_MESSAGE_TO_CLIENT, answer=self._question[2])))

        if self.players_count():
            self._question_timer = threading.Timer(5, self.start_quiz)
            self._question_timer.start()


    def handle_player_answer(self, player_name, is_correct):
        if is_correct:
            message = _get_simple_json_message(quiz_globals.CORRECT_ANSWER_MESSAGE_TO_CLIENT)
            delta_score = self._question[3]
        else:
            message = _get_simple_json_message(quiz_globals.INCORRECT_ANSWER_MESSAGE_TO_CLIENT)
            delta_score = -self._question[3]

        self._send_all_players(message)
        self._change_player_score(player_name, delta_score)
        self.show_answer()


    def check_players_answer(self, player_name, answer):
        self._question_timer.cancel()
        self.handle_player_answer(player_name, answer.lower() == self._question[2].lower().strip(' ."\''))


    def wait_answer(self, player_name):
        self._question_timer.cancel()
        self._send_all_players_except_one(player_name, _get_simple_json_message(quiz_globals.STOP_ANSWER_MESSAGE_TO_CLIENT))
        self._question_timer = threading.Timer(10, functools.partial(self.handle_player_answer, is_correct=False, player_name=player_name))