class Round:
    def __init__(self):
        pass

    def start(self):
        print("Round started.")

    def end(self):
        print("Round ended.")
        pass

class Game:
    """
            Base Game Class

            All "games" should derive from this basic interface


            A game is a section of the gameshow, it can have multiple
            rounds or steps
    """
    def __init__(self, rounds, name: str, static_page=None):
        self.static_page = static_page or name
        self.rounds: list = rounds
        self.name = name
    
    def next_round(self):
        if len(self.rounds) > 0:
            if self.cur_round:
                self.cur_round.end()
            self.cur_round = self.rounds[0]
            self.rounds.remove(self.rounds[0])
    