import threading
import simplejson
from geventwebsocket import WebSocketError
import quiz_globals
import functools
from questions_cache import get_question_iter

def _get_simple_json_message(message):
    return simplejson.dumps(dict(type=message))


class Room():
    def __init__(self):
        self._players_sockets = {}
        self._players_scores = {}
        self._timer = None
        self._question = None
        self._question_iterable = get_question_iter()
        self._answered_players = []


    def add_player(self, player_name, player_socket):
        self._players_sockets[player_name] = player_socket
        self._players_scores[player_name] = 0
        self._change_player_score(player_name, 0)# show new player in scores


    def players_count(self):
        return len(self._players_sockets)


    def remove_player(self, player_name):
        del self._players_sockets[player_name]
        del self._players_scores[player_name]


    def _send_all_players(self, data, excluded_names=None):
        if excluded_names is None:
            for player_socket in self._players_sockets.values():
                try:
                    player_socket.send(data)
                except WebSocketError:
                    pass#todo add autodelete players
        else:
            for player_name in self._players_sockets:
                if player_name not in excluded_names:
                    try:
                        self._players_sockets[player_name].send(data)
                    except WebSocketError:
                        pass#todo add autodelete players


    def start_new_task(self, task, time):
        if self._timer is not None:
            self._timer.cancel()

        self._timer = threading.Timer(time, task)
        self._timer.start()


    def _change_player_score(self, player_name, delta_score):
        self._players_scores[player_name] += delta_score
        data = simplejson.dumps(dict(type=quiz_globals.SCORES_CHANGED_MESSAGE_TO_CLIENT, scores=self._players_scores))
        self._send_all_players(data)


    def start_quiz(self, new_round=True):
        if new_round:
            self._question = next(self._question_iterable)

        question_data = simplejson.dumps(
            dict(type=quiz_globals.QUESTION_MESSAGE_TO_CLIENT, topic=self._question[0], question=self._question[1],
                price=self._question[3]))

        if new_round:
            self._send_all_players(question_data)
        else:
            self._send_all_players(question_data, self._answered_players)

        self.start_new_task(self.start_new_round, 10)


    def start_new_round(self):
        self.show_answer()

        if self.players_count():
            self._answered_players = []
            self.start_new_task(self.start_quiz, 5)


    def show_answer(self, player_name=None):
        message = simplejson.dumps(dict(type=quiz_globals.ANSWER_MESSAGE_TO_CLIENT, answer=self._question[2]))

        if player_name is None:
            self._send_all_players(message)
        else:
            self._players_sockets[player_name].send(message)


    def handle_player_answer(self, player_name, is_correct):
        if is_correct:
            message = _get_simple_json_message(quiz_globals.CORRECT_ANSWER_MESSAGE_TO_CLIENT)
            delta_score = self._question[3]
        else:
            message = _get_simple_json_message(quiz_globals.INCORRECT_ANSWER_MESSAGE_TO_CLIENT)
            delta_score = -self._question[3]

        self._players_sockets[player_name].send(message)
        self._change_player_score(player_name, delta_score)

        if not is_correct:
            self.show_answer(player_name)
            self._answered_players.append(player_name)

            if self.players_count() == len(self._answered_players):
                self.start_new_round()
            else:
                self.start_quiz(False)
        else:
            self.start_new_round()


    def check_players_answer(self, player_name, answer):
        self.handle_player_answer(player_name, answer.lower() == self._question[2].lower().strip(' ."\''))


    def wait_answer(self, player_name):
        self._send_all_players(_get_simple_json_message(quiz_globals.STOP_ANSWER_MESSAGE_TO_CLIENT), [player_name])
        handle_incorrect_answer = functools.partial(self.handle_player_answer, is_correct=False, player_name=player_name)
        self.start_new_task(handle_incorrect_answer, 10)