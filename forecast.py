import csv
import pdb
import picks
import synonyms
from game import Game
from round import Round
from bracket import Bracket
from team import Team


def sort_region(region):
    return [region[0], region[7], region[4], region[3], 
            region[5], region[2], region[6], region[1]]

def sort_first_games(first_games):
    m = first_games
    mp = sorted(m, key=lambda k:k['team0'].seed)
    mpp = sorted(mp, key=lambda k:k['team0'].region)

    East = sort_region(mpp[0:8])
    Midwest = sort_region(mpp[8:16])
    South = sort_region(mpp[16:24])
    West = sort_region(mpp[24:32])
     
    return East + West + South + Midwest 

def csv_row2dict(row, fieldnames):
    data = {}
    i = 0
    for field in row:
        field = field.strip()
        try:
            curr = float(field)
        except:
            if field == 'False':
                curr = False
            elif field == 'True':
                curr = True
            else:
                curr = field
        data[fieldnames[i]] = curr
        i = i + 1
    return data

class Forecast:
    def __init__(self, forecast_file, truth_file=''):
        self.forecast_file = forecast_file
        self.truth_file = truth_file
        self.idmap = {}
        self.teams = {} # dict id -> Team
        self.first_games = []

        self.read_forecast(forecast_file)
        self.make_name_to_id_lookup()
        if len(truth_file) > 0:
            self.add_truth(truth_file)
        self.hardcode_first_round() 
        self.find_first_games()

    def add_truth(self, truth_file):
        # Expects csv with a header row and then
        # two columns, Name and Final Round
        with open(truth_file, 'r') as f:
            reader = csv.reader(f, delimiter=',')
            header = reader.__next__()
            for row in reader:
                name, final_round = row[0], int(row[1])
                curr_id = self.name_to_id(name)
                self.teams[curr_id].update_final_round(final_round)
    
    def hardcode_first_round(self):
        # 11a 2057 East Belmont 
        # 11b 218 East Temple 

        # 16a 161 West Fairleigh Dickinson
        # 16b 2504 West Prairie View 

        # 16b 2449 East North Dakota State 
        # 16a 2428 East North Carolina Central 

        # 11a 9 West Arizona State 
        # 11b 2599 West St. John's (NY) 

        playin_winners = [2057, 161, 2449, 9]
        playin_losers = [218, 2504, 2428, 2599]

        for t_id in playin_winners:
            self.teams[t_id].seed = float(self.teams[t_id].seed[0:2])
            self.teams[t_id].playin_flag = 0
        for t_id in playin_losers:
            self.teams.pop(t_id)

        for team_id, team in self.teams.items():
            if team.playin_flag > 0:
                print(team.seed, team_id, team.region, team.name)

    def find_first_games(self):
        teams = self.teams
        games = []
        for teamid in teams:
            team = teams[teamid]
            if team.playin_flag:
               print(team.name)
            else:
                if team.seed <= 8:
                    for teamid2 in teams:
                        team1 = teams[teamid2]
                        if team1.region == team.region:
                            if not team1.playin_flag:
                                if team.seed + team1.seed == 17:
                                    games.append({"team0":team, "team1":team1, "round": 1}) 
        first_games = sort_first_games(games)
        self.first_games = Round(first_games)

    def read_forecast(self, fname):
        teams = {}
        with open(fname, 'r') as f:
            reader = csv.reader(f, delimiter=',')
            header = reader.__next__()
            id_idx = header.index('team_id')
            for row in reader:
                if row[0] == 'mens':
                    curr_id = int(row[id_idx])
                    team_dict = csv_row2dict(row, header)
                    teams[curr_id] = Team(team_dict)
        self.teams = teams

    def make_name_to_id_lookup(self):
        for teamid in self.teams:
            team = self.teams[teamid]
            self.idmap[team.name.lower()] = team.id

    def name_to_id(self, name):                
        name = name.lower().strip()
        if name in synonyms.synonyms:
            name = synonyms.synonyms[name].lower().strip()
        if name in self.idmap:
            return int(self.idmap[name])
        else:
            print('"{}" not found in forecast bracket'.format(name)) 
            pdb.set_trace()
            raise("Error")

    def write_truth_file(self, outfile):
        with open(outfile, 'wt') as fo:
            fo.write('Name, Final Round\n')
            for game in self.first_games.games:
                game.team0.write_to_truth_file(fo)
                game.team1.write_to_truth_file(fo)

 


