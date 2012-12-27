import threading
import simplejson
import quiz_globals
import functools
from questions_cache import get_question_iter

def _get_simple_json_message(message):
    return simplejson.dumps(dict(type=message))

class Room():
    def __init__(self):
        self._players = []
        self._question_timer = None
        self._question = None
        self._question_iter = get_question_iter()


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
        self._question = next(self._question_iter)
        question_data = simplejson.dumps(
            dict(type = quiz_globals.QUESTION_MESSAGE_TO_CLIENT, topic=self._question[0], question=self._question[1]))
        self._send_all_players(question_data)
        self._question_timer = threading.Timer(12, self.show_answer)
        self._question_timer.start()


    def show_answer(self):
        self._send_all_players(simplejson.dumps(dict(type=quiz_globals.ANSWER_MESSAGE_TO_CLIENT, answer='answer')))

        if self.players_count():
            self._question_timer = threading.Timer(5, self.start_quiz)
            self._question_timer.start()


    def handle_player_answer(self, player, is_correct):
        if is_correct:
            player.send(quiz_globals.CORRECT_ANSWER_MESSAGE_TO_CLIENT)
        else:
            player.send(quiz_globals.INCORRECT_ANSWER_MESSAGE_TO_CLIENT)
        self.show_answer()


    def check_players_answer(self, player, answer):
        self._question_timer.cancel()
        self.handle_player_answer(player, answer.lower() == self._question[2].lower())


    def wait_answer(self, player):
        self._question_timer.cancel()
        self._send_all_players_except_one(player, _get_simple_json_message(quiz_globals.STOP_ANSWER_MESSAGE_TO_CLIENT))
        self._question_timer = threading.Timer(10, functools.partial(self.handle_player_answer, is_correct=False, player=player))