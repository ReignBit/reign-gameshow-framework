from game import Game, Round

class TriviaGame(Game):
    def __init__(self):
        self.rounds = [
            Round(),
            Round(),
            Round()
        ]
        super().__init__(self.rounds, "Trivia Game")