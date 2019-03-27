from game import Game
import pdb

class Round:
    def __init__(self, games, rnd=1, favorite=False):
        self.favorite = favorite
        self.games = []
        self.rnd = rnd
        for game in games:
            self.games.append(Game(game, self.rnd))

    def next_round(self):
        if len(self.games) < 2:
            return False

        games = []
        for i in range(len(self.games)//2):
            team1 = self.games[2*i].get_winner()
            team2 = self.games[2*i+1].get_winner()
            games.append((team1, team2)) 

        return Round(games, rnd=self.rnd + 1, favorite=self.favorite)

    def summary(self):
        out = ""
        for game in self.games:
           out += game.summary() + '\n'
        return out

    def __str__(self):
        out = ""
        for item in vars(self).items():
            if isinstance(item[1], list):
                out += '  {:12} [({})]\n'.format(item[0], len(item[1]))
            else:
                out += '  {:12} {}\n'.format(item[0], item[1])
        return out