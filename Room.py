import threading

__author__ = 'atanana'

class Room():
    def __init__(self):
        self._players = []

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

    def start_quiz(self):
        self._send_all_players('startQuiz')

        def on_timer():
            self.start_quiz()

        if self.players_count():
            threading.Timer(20, on_timer).start()