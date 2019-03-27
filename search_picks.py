import pickle
import numpy as np
from forecast import Forecast, Bracket
import gen_brackets
import pdb
import time
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from scipy.stats import rankdata 

def team_summary(team):
    return '{:5} {:8} {:12} {:6}'.format(team['team_seed'], team['team_region'], team['team_name'][0:12], team['team_id'])


def write_picks(picks):
    forecast = Forecast('./forecast/fivethirtyeight_ncaa_forecasts.csv')
    n = 32
    i = 0
    for pick in picks:
        print(team_summary(forecast.teams[pick]))
        i += 1
        if i == n:
            print('------------')
            n = n/2
            i = 0

def score_per_round_to_score_per_game(score):
    score_array = np.zeros(63)
    n = 32
    i = 0
    j = 0
    while n >= 1:
        n = int(n)
        score_array[i:i+n] = score[j]
        j += 1
        i += n
        n = n/2
    return score_array

def score_all_picks(picks_array, brackets, use_bonus):
    Npicks = picks_array.shape[0]
    Nbrackets = brackets['ids'].shape[0]  
    total = np.zeros((Nbrackets, Npicks))
    score = np.zeros((Nbrackets, Npicks))
    bonus = np.zeros((Nbrackets, Npicks))
    for i in range(Npicks):
        total[:,i], score[:,i], bonus[:,i] = score_brackets(picks_array[i], brackets, use_bonus)
    return total, score, bonus

def score_brackets(picks, brackets, scoring_type):

    Npicks = picks.shape[0]
    Nbrackets = brackets['ids'].shape[0]
    picks = np.expand_dims(picks, axis=0)
    bracket_ids = np.expand_dims(brackets['ids'], axis=1)
    check = picks == bracket_ids
   
    if scoring_type == 'family': 
        score_per_round = [10, 20, 40, 80, 120, 160]
        bonus_multiplier = [5, 10, 20, 30, 40, 50]
    elif scoring_type == 'spacex':
        score_per_round = [1, 2, 4, 8, 16, 32]
        # bonus_multiplier = [1,1,2,2,3,3]
        bonus_multiplier = [1,1,3,4,5,6]
    else:
        print('scoring type not recognized')
        pdb.set_trace()

    score_per_game = score_per_round_to_score_per_game(score_per_round)
    bonus_multiplier_per_game = score_per_round_to_score_per_game(bonus_multiplier)
    score = score_per_game * check

    seed_diffs = brackets['seed_diffs']
    seed_diffs[seed_diffs < 0] = 0
    seed_diffs = np.expand_dims(seed_diffs, axis=1)
    bonus = seed_diffs * check * bonus_multiplier_per_game
    score = np.sum(score, axis=2).squeeze()
    bonus = np.sum(bonus, axis=2).squeeze()
    total = score + bonus
    return total, score, bonus

def random_picks(forecast):
    picks_as_bracket = Bracket(forecast.first_games)
    picks = np.zeros(63, dtype='uint16')
    i = 0
    for rd in picks_as_bracket.bracket:
        for game in rd:
            picks[i] = game['win_id']
            i += 1
    return picks

def plot_i(i, picks, total, avg, perc95, top5_cnt, name, write_to_file):
    if write_to_file:
        with open("brackets.txt", 'at') as f:
            z = picks[i,:]
            for x in z:
                f.write(str(x)+ ", ")
            f.write("\n")
            f.write("# {:6.1f} {:6.1f} {:6.3f}\n".format(
                avg[i], perc95[i], top5_cnt[i]))

    print("{:6.0f} {:6.0f} {:6.0f} {:6.3f}".format(
        i, avg[i], perc95[i], top5_cnt[i]))
    # plt.hist(total[:,i], bins = 50, histtype=u'step', label=name)
    z = total[:,i]
    z.sort()
    plt.plot(np.linspace(0,1,len(z)), z, label=name)

def read_top_picks():
    with open("brackets.txt") as fp:
        txt = fp.readlines()
    top_picks = np.zeros((len(txt), 63), dtype='uint16')
    i = 0
    for line in txt:
        if line[0] is not '#':
            split = line.split(', ')
            try:
                top_picks[i,:]= np.array([int(float(x)) for x in split[:-1]])
            except:
                pdb.set_trace()
            i += 1
    top_picks = top_picks[:i,:]
    return top_picks

def search(Npicks=10000, picks_in = np.zeros((0,63)), fname = '5050.csv'):
    # picks = random_picks(forecast)
    picks, _ = gen_brackets.gen_brackets(Npicks-1, fname=fname)
    picks = np.vstack((picks, picks_in))
    picks = np.vstack((picks, baseline))
    t1 = time.time()
    total, _, _ = score_all_picks(picks, brackets, use_bonus)
    print('time to score:', time.time() - t1)
    avg = total.mean(axis=0)
    perc95 = np.percentile(total, 95, axis=0)
    ranks = np.zeros_like(total)
    for i in range(total.shape[0]):
        ranks[i,:] = rankdata(total[i,:])
    top5 = ranks > 0.95*(picks.shape[0])
    top5_cnt = top5.sum(axis=0)/Nbrackets
    i1 = avg.argmax()
    i2 = perc95.argmax()
    i3 = top5_cnt.argmax()
    print('{:>6s} {:>6s} {:>6s} {:>6s}'.format('idx', 'mean', '95%', 'top5%'))
    plot_i(i1, picks, total, avg, perc95, top5_cnt, 'max mean', True)
    plot_i(i2, picks, total, avg, perc95, top5_cnt, 'max 95 percentile', i2 != i1)
    plot_i(i3, picks, total, avg, perc95, top5_cnt, 'most top 5%', i3 != i2 and i3 != i1)
    plot_i(Npicks-1, picks, total, avg, perc95, top5_cnt, 'baseline', False)
    plt.legend()

    # plt.show()
    # pdb.set_trace()
    return picks[i1,:]




