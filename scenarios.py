import os
import copy
from compete import Compete
from forecast import Forecast
from bracket import Bracket
from picks import Picks
import numpy as np
import glob
import pdb

class Scenarios:
    def __init__(self, Nbrackets, pick_ids, forecast, bonus_type, option, results_out_dir, names=''):
        self.results_out_dir = results_out_dir
        self.forecast = forecast
        self.initial_truth_file = self.forecast.truth_file
        self.forecast_file = self.forecast.forecast_file
        if type(option) is str:
            self.results_file = option
            self.write_truth_files()
        elif type(option) is int:
            self.n_rnd = option
            self.write_truth_scenario_files()

        self.competitions = []
        self.truth_files = []

        truth_files = os.listdir(results_out_dir)
        truth_files.sort()
        for truth_file in truth_files:
            if truth_file.endswith(".truth"):
                tf = os.path.join(results_out_dir, truth_file)
                print(tf)
                self.truth_files.append(tf)
                forecast = Forecast(self.forecast_file, tf)
                curr = Compete(pick_ids, forecast, bonus_type, names)
                curr.run_MC(Nbrackets)
                curr.do_calcs()

                self.competitions.append(copy.copy(curr))

    def write_truth_scenario_files(self):
        n_rnd = self.n_rnd
        out_dir = self.results_out_dir
        bracket = Bracket(self.forecast.first_games)
        rnd = bracket.rounds[n_rnd-1]
        self.scenarios = []
        scenario_count = 1
        game_count = 1
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)

        outfile = os.path.join(out_dir, 'scenario00.truth')
        self.scenarios.append(self.initial_truth_file)
        self.forecast.write_truth_file(outfile)
        for game in rnd.games:
            team1 = self.forecast.teams[game.teams[0].id]
            team2 = self.forecast.teams[game.teams[1].id]
            if team1.final_round == -1 and team2.final_round == -1:
                outfile = os.path.join(out_dir, 'scenario{:02d}.truth'.format(scenario_count))
                forecast = Forecast(self.forecast_file, self.initial_truth_file)
                winner = game.teams[0].name
                loser  = game.teams[1].name
                forecast.teams[game.teams[1].id].final_round = n_rnd
                self.scenarios.append('Round {} Game {}A: {} defeats {}'.format(n_rnd, game_count, winner, loser))
                forecast.write_truth_file(outfile)
                scenario_count += 1

                outfile = os.path.join(out_dir, 'scenario{:02d}.truth'.format(scenario_count))
                forecast = Forecast(self.forecast_file, self.initial_truth_file)
                winner = game.teams[1].name
                loser  = game.teams[0].name
                forecast.teams[game.teams[0].id].final_round = n_rnd
                self.scenarios.append('Round {} Game {}B: {} defeats {}'.format(n_rnd, game_count, winner, loser))
                forecast.write_truth_file(outfile) 
                scenario_count += 1
            game_count += 1


    def get_game(self, competition):
        truth_file = competition.forecast.truth_file
        if truth_file.find('round') >= 0 and truth_file.find('game') >= 0:
            i = int(truth_file[-14])
            j = int(truth_file[-8:-6])
            if i == 0 and j == 0:
                return "initial"
            else:
                curr_id = self.result_ids[i-1][j-1]
               # bracket = competition.brackets[0]
                bracket = Bracket(competition.forecast.first_games)
                rnd = bracket.rounds[i-1]
                for game in rnd.games:
                    if game.teams[0].id == curr_id:
                        loser =  game.teams[0].name  
                        winner = game.teams[1].name  
                        break
                    if game.teams[1].id == curr_id:
                        loser =  game.teams[1].name  
                        winner = game.teams[0].name  
                        break
                return 'Round {} Game {:02d}: {} defeats {}'.format(i,j,winner, loser)
        elif truth_file.find('scenario') >=0:
            i = int(truth_file[-8:-6])
            return self.scenarios[i]
        else:
            print(truth_file)
            return ''
 
    def write_to_file(self, out_file, order=None):
        if order is None:
            # order = range(0, len(self.competitions[0].pick_names))
            order = self.competitions[0].sort_order()
        out = ''
        with open(out_file, 'wt') as f:
            out += 'Probability of Winning\n'
            out += self.names(order)
            for c in self.competitions:
                out += '{:10},'.format(self.get_game(c))
                for i in order:
                    out += '{:10.4f},'.format(c.pwin[i]*100)     
                out += '\n'
            out += '\n'
            out += 'Probability of Losing\n'
            out += self.names(order)
            for c in self.competitions:
                out += '{:10},'.format(self.get_game(c))
                for i in order:
                    out += '{:10.4f},'.format(c.plose[i]*100)
                out += '\n'
            out += '\n'
            out += 'Best Finish\n'
            out += self.names(order)
            for c in self.competitions:
                out += '{:10},'.format(self.get_game(c))
                for i in order:
                    out += '{:6.0f},'.format(c.best_finish[i])
                out += '\n'
            out += '\n'
            out += 'Worst Finish\n'
            out += self.names(order)
            for c in self.competitions:
                out += '{:10},'.format(self.get_game(c))
                for i in order:
                    out += '{:6.0f},'.format(c.worst_finish[i])
                out += '\n'
            out += '\n'
            out += 'Min Score\n'
            out += self.names(order)
            for c in self.competitions:
                out += '{:10},'.format(self.get_game(c))
                for i in order:
                    out += '{:6.0f},'.format(c.min_scores[i])
                out += '\n'
            out += '\n'
            out += 'Max Score\n'
            out += self.names(order)
            for c in self.competitions:
                out += '{:10},'.format(self.get_game(c))
                for i in order:
                    out += '{:6.0f},'.format(c.max_scores[i])     
                out += '\n'
            f.write(out)

    def names(self,order):
        out = ','
        for i in order:
            out += '{},'.format(self.competitions[0].pick_names[i])
        out += '\n'
        return out
        

    def write_truth_files(self):
        results_file = self.results_file
        forecast = self.forecast
        out_dir = self.results_out_dir
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        forecast = self.forecast 
        i = -1
        count = 1
        results = []
        result_ids = []
        outfile = os.path.join(out_dir, 'round0_game00.truth')
        forecast.write_truth_file(outfile)
        with open(results_file, 'r') as f:
            for line in f:
                if line[0] == '-':
                    results.append([])
                    result_ids.append([])
                    i += 1
                    count = 1
                else:
                    results[i].append(line.strip())
                    curr_id = forecast.name_to_id(line)
                    result_ids[i].append(curr_id)
                    if curr_id:
                        forecast.teams[curr_id].final_round = i+1
                        outfile = os.path.join(out_dir, 'round{}_game{:02d}.truth'.format(i+1,count))
                        forecast.write_truth_file(outfile)
                        count += 1
        self.results = results
        self.result_ids = result_ids



picks_dir = 'family'
# picks_dir = 'spacex'

forecast_file = './forecast/fivethirtyeight_ncaa_forecasts.csv'
# forecast_file = './forecast/5050.csv'

truth_file = ''
# truth_file = './truth/rd1.truth'
# truth_file = './truth/rd2.truth'
# truth_file = './truth/scenario.truth'

bonus_type = picks_dir

forecast = Forecast(forecast_file, truth_file)

all_picks = []
picks_files = glob.glob(picks_dir + '/*.picks')
if len(picks_files) > 0: 
    for file in picks_files:
        all_picks.append(Picks(file))
else:
    all_picks = yahoo_parsing.run_yahoo_parsing(picks_dir)

names = []
pick_ids = np.zeros((len(all_picks), 63), dtype='uint16')
for j, curr_picks in enumerate(all_picks):
    pick_ids[j,:] = curr_picks.convert_to_id(forecast) 
    names.append(curr_picks.name)

results_out_dir = './tmp2/'
# option = 3
option = 'losers.schedule'
Nbrackets = 10000
sce = Scenarios(Nbrackets, pick_ids, forecast, bonus_type, option, results_out_dir, names)
sce.write_to_file('tmp_out2')

