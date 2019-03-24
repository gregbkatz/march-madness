import pickle
from forecast import Forecast, resolve_bracket
import numpy as np

def baseline():
    forecast = Forecast('fivethirtyeight_ncaa_forecasts.csv')
    bracket = resolve_bracket(forecast.first_games, favorite=True)
    ids, seed_diffs = convert_bracket(bracket)
    return ids, seed_diffs

def gen_brackets(N, fname = 'fivethirtyeight_ncaa_forecasts.csv', verbose = False):
    forecast = Forecast('fivethirtyeight_ncaa_forecasts.csv')
    ids = np.zeros((N, 63), dtype='uint16')
    seed_diffs = np.zeros((N, 63), dtype='int8')
    for i in range(N):
        if verbose and i % 1000 == 0:
            print(i)
        bracket = resolve_bracket(forecast.first_games)
        ids[i,:], seed_diffs[i,:] = convert_bracket(bracket)
    return ids, seed_diffs

def convert_bracket(bracket):
    ids = np.zeros(63, dtype='uint16')
    seed_diffs = np.zeros(63, dtype='int8')
    i = 0
    for rd in bracket:
        for game in rd:
            ids[i] = game['win_id']
            seed_diffs[i] = game['seed_diff']
            i += 1 
    return ids, seed_diffs

def write_brackets_to_pickle(N):
    ids, seed_diffs = gen_brackets(N)
    pickle_filename = "mc_brackets_{}.p".format(N)
    with open(pickle_filename, 'wb') as fp:
        pickle.dump({'ids':ids, 'seed_diffs':seed_diffs}, fp)

