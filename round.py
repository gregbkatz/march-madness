from game import Game

class Round:
    def __init__(self, games, favorite=False):
        self.favorite = favorite
        self.games = []
        for game in games:
            self.games.append(Game(game))

    def next_round(self):
        games = []
        skip = True
        last_team = {}
        for game in self.games:
            if game.result:
                team = game.team1
            else:
                team = game.team0
            if skip:
                skip = False
            else:
                rnd = game.round
                games.append({"team0":last_team, "team1":team, "round":rnd+1})
                skip = True

            last_team = team
        return Round(games, self.favorite)


    def resolve(self):
        for game in self.games:
            game.resolve()