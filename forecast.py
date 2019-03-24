import csv
from scipy.special import erfinv, erf
# import numpy as np
from random import uniform

# region_order = {'East':100, 'West':300, 'South':400, 'Midwest':200, }
def calc_win_prob(game):
    diff = game['team1']['team_rating'] - game['team2']['team_rating']
    return 0.5*(1+erf(diff/10/2**0.5))

def resolve_game(game, sample):
# returns index of winning team
# sample must be between 0 and 1
# For monte carlo, sample should be uniformly distributed
# For favorite to win use 1
# For higher rated to win use 0.5
    
    if 'final_round' in game['team1']:
        t1_frnd = game['team1']['final_round']
    else:
        t1_frnd = -1
    
    if 'final_round' in game['team2']:
        t2_frnd = game['team2']['final_round']
    else:
        t2_frnd = -1

    rnd = game['round']    
    if t1_frnd == rnd:
        if t2_frnd > rnd or t2_frnd == -1:
            return 1
        else:
            print(game_summary(game))
    if t2_frnd == rnd:
        if t1_frnd > rnd or t1_frnd == -1:
            return 0
        else:
            print(game_summary(game)) 

    # something doesn't add up
    if t1_frnd > rnd:
        if t2_frnd > rnd:    
            print(game_summary(game))
        else:
            return 0

    if t2_frnd > rnd:
        return 1
 
    if sample <= game['p_win']:
        return 0 # first team wins
    else:
        return 1 # second team wins

def resolve_round(games, favorite=False):
    i = 0
    for game in games:
        games[i]['p_win'] = calc_win_prob(game)
        sample = 0.5 if favorite else uniform(0,1)
        games[i]['result'] = resolve_game(game, sample)
        if games[i]['result']:
            games[i]['win_id'] = games[i]['team2']['team_id']
            games[i]['seed_diff'] = games[i]['team2']['team_seed'] - games[i]['team1']['team_seed']
        else:
            games[i]['win_id'] = games[i]['team1']['team_id']
            games[i]['seed_diff'] = games[i]['team1']['team_seed'] - games[i]['team2']['team_seed']
        i = i+1
    return games

def new_round(last_round):
    games = []
    skip = True
    last_team = {}
    for game in last_round:
        if game['result']:
            team = game['team2']
        else:
            team = game['team1']
        if skip:
            skip = False
        else:
            rnd = game['round']
            games.append({"team1":last_team, "team2":team, "round":rnd+1})
            skip = True

        last_team = team
    return games

   
def resolve_bracket(games, favorite=False):
    bracket = [games]
    i = 0
    while True:
        bracket[i] = resolve_round(bracket[i], favorite)
        if len(bracket[i]) <= 1:
            break
        bracket.append(new_round(bracket[i]))
        i = i+1 
               
    return bracket 

def sort_region(region):
    return [region[0], region[7], region[4], region[3], region[5], region[2], region[6], region[1]]

class Forecast:
    def __init__(self, fname, truth_file=''):
        self.get_synonyms()
        self.read_forecast(fname)
        self.make_name_to_id_lookup()
        self.truth_file = truth_file
        if truth_file:
            self.add_truth(truth_file)
        self.hardcode_first_round() 
        self.find_first_games()
#        self.check_fit()
        self.sort_first_games()
#        self.rd1 = resolve_round(self.first_games)
#        self.rd2 = new_round(self.rd1)
#        self.bracket = resolve_bracket(self.first_games)

    def add_truth(self, truth_file):
        truth_list = []
        with open(truth_file, 'r') as f:
            reader = csv.reader(f, delimiter=',')
            header = []
            for row in reader:
                if not header:
                    header = row
                else:
                    row[1] = int(row[1])
                    truth_list.append(row)
                    curr_id = name_to_id(row[0], self.idmap, self.synonyms)
                    if curr_id:
                        self.teams[curr_id]['final_round'] = int(row[1])
                    else:
                        print('WTF')
        self.truth_list = truth_list

    def write_first_round_to_file(self, fname='first_round.csv'):
        with open(fname, 'wt') as f:
            for game in self.first_games:
                f.write(game['team1']['team_name'] + '\n')
                f.write(game['team2']['team_name'] + '\n')
    
    def sort_first_games(self):
        m = self.first_games
        mp = sorted(m, key=lambda k:k['team1']['team_seed'])
        mpp = sorted(mp, key=lambda k:k['team1']['team_region'])
        #print(mpp)
        #print(len(mpp))
        East = sort_region(mpp[0:8])
        Midwest = sort_region(mpp[8:16])
        South = sort_region(mpp[16:24])
        West = sort_region(mpp[24:32])
         
        self.first_games = East + West + South + Midwest 


    def hardcode_first_round(self):
# 11a 2057 East Belmont ***
# 11a 9 West Arizona State ***
# 11b 218 East Temple xxx
# 11b 2599 West St. John's (NY) xxx
# 16b 2449 East North Dakota State ***
# 16b 2504 West Prairie View xxx
# 16a 161 West Fairleigh Dickinson ***
# 16a 2428 East North Carolina Central xxx

        playin_losers = [218, 2599, 2504, 2428]
        playin_winners = [2057, 9, 2449, 161]
        for t_id in playin_losers:
            self.teams.pop(t_id)
        for t_id in playin_winners:
            self.teams[t_id]['team_seed'] = float(self.teams[t_id]['team_seed'][0:2])
            self.teams[t_id]['playin_flag'] = 0

        for team_id, team in self.teams.items():
            if team['playin_flag'] > 0:
                print(team['team_seed'], team_id, team['team_region'], team['team_name'])

    def check_fit(self):
        games = self.first_games
        i = 0
        for game in games:
            diff = game['team1']['team_rating'] - game['team2']['team_rating']
            p_win = game['team1']['rd2_win']

            nsigma = 2**0.5*erfinv(2*p_win-1)
            sigma = diff/nsigma
            est = 0.5*(1+erf(diff/10/2**0.5))
            error = est - p_win 

            games[i]['diff'] = diff
            games[i]['nsigma'] = nsigma
            games[i]['sigma'] = sigma
            games[i]['est'] = est
            games[i]['error'] = error

            i = i + 1
        self.first_games = games

    def find_first_games(self):
        teams = self.teams
        games = []
        for teamid in teams:
            team = teams[teamid]
            if team['playin_flag']:
               print(team['team_name'])
            else:
                if team['team_seed'] <= 8:
                    for teamid2 in teams:
                        team2 = teams[teamid2]
                        if team2['team_region'] == team['team_region']:
                            if not team2['playin_flag']:
                                if team['team_seed'] + team2['team_seed'] == 17:
                                    games.append({"team1":team, "team2":team2, "round": 1}) 
        self.first_games = games

    def read_forecast(self, fname):
        teams = {}
        self.forecast_file = fname
        with open(fname, 'r') as f:
            reader = csv.reader(f, delimiter=',')
            header = []
            for row in reader:
                if not header:
                    header = row
                    id_idx = header.index('team_id')
                    # seed_idx = header.index('team_seed')
                    # region_idx = header.index('team_region')
                else:
                    if row[0] == 'mens':
                        curr_id = int(row[id_idx])
                        # try:
                            # seed = int(row[seed_idx])
                        # except:
                            # seed = int(row[seed_idx][:-1])
                        # region = region_order[row[region_idx]]
                        # curr_id = region + seed
                        teams[curr_id] = {}
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
                            teams[curr_id][header[i]] = curr
                            i = i + 1
        self.teams = teams

    def make_name_to_id_lookup(self):
        self.idmap = {}
        for teamid in self.teams:
            team = self.teams[teamid]
            self.idmap[team['team_name'].lower()] = team['team_id']
        
    
    def get_synonyms(self):
        s = {
             'cal': 'california', 
             'wichita st.': 'wichita state',
             'miami': 'miami (fl)', 
             "saint joe's": "saint joseph's",
             'unc': 'north carolina',
             'usc': 'southern california',
             'uva': 'virginia',
             'uconn': 'connecticut',
             's. dakota st.': 'south dakota state',
             'unc-wilm.': 'north carolina-wilmington',
             'n. iowa': 'northern iowa',
             'vcu': 'virginia commonwealth',
             'chatt.': 'chattanooga',
             'w. virginia': 'west virginia',
             'ark.-lr': 'arkansas-little rock',
             'virginia com': 'virginia commonwealth',
             'north caroli': 'north carolina',
             'west virgini': 'west virginia',
             'michigan sta': 'michigan state',
             'south dakota': 'south dakota state',
             'wichita stat': 'wichita state',
             'northern iow': 'northern iowa',
             'stephen f. a': 'stephen f. austin',
             'arkansas-lit': 'arkansas-little rock',
             'southern cal': 'southern california',
              'florida gulf': 'florida gulf coast',
             'n. c. wilmington': 'north carolina-wilmington',
             'fresno st.': 'fresno state',
             'n. carolina': 'north carolina',
             'ar little rock': 'arkansas-little rock',
             'iowa st.': 'iowa state',
             'michigan st.': 'michigan state',
             'sf austin': 'stephen f. austin',
             'wichita st': 'wichita state',
             'n carolina': 'north carolina',
             'michigan st': 'michigan state',
             'oregon st.': 'oregon state',
             'n.c. wilmington': 'north carolina-wilmington',
             's.f. austin': 'stephen f. austin',
             "st. joseph\\'s": "saint joseph's",
             "texas am": "texas a&m",
             "saint joes": "saint joseph's",
             "pitt": "pittsburgh",
             "ky": "kentucky",
             "mich st": "michigan state",
             "okla": "oklahoma",
             "west v": "west virginia",
             "nova": "villanova",
             "iowa st": "iowa state",
             "ar-little rock": "arkansas-little rock",
             "zona": "arizona",
             "oregon st": "oregon state",
             "unc wilmington": "north carolina-wilmington",
             "unc-wilm": "north carolina-wilmington",
             "fgcu": "florida gulf coast",
             "unc-ash.": "north carolina-asheville",
             "csu bakers.": "cal state bakersfield",
             "mid. tenn.": "middle tennessee",
             "saint joseph": "saint joseph's", 
             "saint mary\\'s": "saint mary's (ca)",
             "saint mary's": "saint mary's (ca)",
             "southern met": "southern methodist",
             "south caroli": "south carolina",
             "new mexico s": "new mexico state",
             "virginia tec": "virginia tech", 
             "northern ken": "northern kentucky", 
             "florida stat": "florida state",
             "middle tenne": "middle tennessee",
             "oklahoma sta": "oklahoma state",
             "east tenness": "east tennessee state",
             "jacksonville": "jacksonville state",
             "texas southe": "texas southern",
             "mount st. ma": "mount st. mary's",
             "florida st.": "florida state",
             "smu": "southern methodist",
             "middle tenn. st.": "middle tennessee",
             "fla gulf coast": "florida gulf coast",
             "e. tennessee st.": "east tennessee state",
             "kansas st.": "kansas state",
             "n. mex. st.": "new mexico state",
             "st. mary\\'s": "saint mary's (ca)",
             "oklahoma st.": "oklahoma state"
             }

 
        self.synonyms = s 


