import search_picks
import gen_brackets

do_round2 = True
if do_round2:
    pickle_filename = 'mc_brackets_10000.p'
    top_picks = search_picks.read_top_picks()
    fname = 'fivethirtyeight_ncaa_forecasts.csv'
    n_iters = 1
    Npicks = 10000
else: 
    pickle_filename = 'mc_brackets_1000.p'
    top_picks = np.zeros((0,63))
    fname = '5050.csv'
    n_iters = 1000
    Npicks = 500000

with open(pickle_filename, 'rb') as fp:
    brackets = pickle.load(fp)
Nbrackets = brackets['ids'].shape[0]

use_bonus = True
baseline, _ = gen_brackets.baseline()
baseline_score = search_picks.score_brackets(baseline, brackets, use_bonus)

for i in range(n_iters):
    picks = search_picks.search(Npicks = Npicks, picks_in=top_picks, fname=fname)
    if do_round2:
        search_picks.write_picks(picks)