
class Bracket:
    def __init__(self, first_round, favorite=False):
        self.rounds = [first_round]
        i = 0
        while True:
            self.rounds[i].resolve()
            if len(self.rounds[i].games) <= 1:
                break
            self.rounds.append(self.rounds[i].next_round())
            i = i+1 