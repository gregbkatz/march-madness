import numpy as np
import time 
import pdb
import gen_brackets
import search_picks
from scipy.stats import rankdata 

def convert_picks_to_id(picks, forecast):
    pick_ids = [] 
    for rd in picks:
        for pick in rd:
            pick_ids.append(forecast.name_to_id(pick))
    return pick_ids

def probability_matrix(ranks):
    shp = np.shape(ranks)
    pmat = np.zeros((shp[1], shp[1]))
    for i in range(0, shp[1]): # competitor
        curr = ranks[:,i]
        for j in range(0, shp[1]): # rank
            pmat[i][j] = len(curr[curr==j+1])
    pmat = pmat/shp[0]
    return pmat

class Compete:
    def __init__(self, picks, forecast, bonus_type):
        self.forecast = forecast
        self.picks = picks

        self.bonus_type = bonus_type
 
        j = 0
        self.pick_ids = np.zeros((len(picks), 63), dtype='uint16')
        for j in range(len(self.picks)):
            self.pick_ids[j,:] = convert_picks_to_id(self.picks[j].picks, self.forecast) 

        #for picks in self.picks:
        #    check_picks(picks.picks)

    def run_MC(self, ncases, verbose=True):
        
        ids, seed_diffs = gen_brackets.gen_brackets(ncases, self.forecast.forecast_file, self.forecast.truth_file)
        brackets = {'ids':ids, 'seed_diffs':seed_diffs}
        scores, no_bonus, bonus = search_picks.score_all_picks(self.pick_ids, brackets, self.bonus_type)
                  
        ranks = np.zeros((ncases, len(self.picks)))
        ranks2 = np.zeros((ncases, len(self.picks)))     
        for i in range(scores.shape[0]):
            ranks[i,:]  = len(self.picks) + 1 - rankdata(scores[i,:], 'max')
            ranks2[i,:] = len(self.picks) + 1 - rankdata(scores[i,:], 'min')

        print('Start Calcs')
        medians = np.median(scores, axis=0)
        pmat = probability_matrix(ranks)
        min_scores = np.min(scores, axis=0)
        min_no_bonus = np.min(no_bonus, axis=0)
        min_bonus = np.min(bonus, axis=0)
        max_scores = np.max(scores, axis=0)
        max_no_bonus = np.max(no_bonus, axis=0)
        max_bonus = np.max(bonus, axis=0)
        pwin = pmat[:,0]      
        pmat2 = probability_matrix(ranks2)
        plose = pmat2[:,-1]
        best_finish = np.min(ranks, axis=0)
        worst_finish = np.max(ranks2,axis=0)
        curr_order = np.argsort(min_scores)
        curr_order = curr_order[::-1]
        mean_finish = np.mean(ranks, axis=0)
        median_finish = np.median(ranks, axis=0)
        print('Finish Calcs')
        # self.brackets = brackets
        # self.bracket_arrays = bracket_arrays
        self.scores = scores 
        self.no_bonus = no_bonus
        self.bonus = bonus
        self.ranks = ranks 
        self.ncases = ncases
        self.medians = medians
        self.pmat = pmat
        self.min_scores = min_scores
        self.min_no_bonus = min_no_bonus
        self.min_bonus = min_bonus
        self.max_scores = max_scores
        self.max_no_bonus = max_no_bonus
        self.max_bonus = max_bonus
        self.pwin = pwin
        self.pmat2 = pmat2
        self.plose = plose
        self.best_finish = best_finish
        self.worst_finish = worst_finish
        self.curr_order = curr_order
        self.mean_finish = mean_finish
        self.median_finish = median_finish


    def analyze_brackets(self):
        teams = self.forecast.teams
        self.p_win = np.zeros((len(teams), len(self.bracket_arrays)))
        i = 0
        team_ids = [] 
        for team_id in teams:
            j = 0
            team_ids.append(team_id)
            for ba in self.bracket_arrays:
                p = probability_in_round(ba, team_id)
                self.p_win[i,j] = p 
                j += 1
            i += 1

        p_win_sort = self.p_win
        full_sort_idx = np.arange(0, len(teams)) 
        for i in range(0,5):
            sort_idx = np.argsort(p_win_sort[:,i])
            p_win_sort = p_win_sort[sort_idx,:]
            full_sort_idx = full_sort_idx[sort_idx]
        full_sort_idx = full_sort_idx[::-1]
        for i in full_sort_idx: 
            out = '{:30}'.format(teams[team_ids[i]]['team_name'])
            for j in range(0,len(self.p_win[i,:])):            
                out += '{:4.0f}'.format(self.p_win[i][j]*100)
            print(out)