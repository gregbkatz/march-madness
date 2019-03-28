import search_picks
from forecast import Forecast
import numpy as np
import pdb

scoring_type = 'family'
do_round2 = True
brackets_forecast_file = './forecast/fivethirtyeight_ncaa_forecasts.csv'
if do_round2:
    top_picks = search_picks.read_top_picks()
    picks_forecast_file = './forecast/fivethirtyeight_ncaa_forecasts.csv'
    n_iters = 1
    Npicks = 5000
    Nbrackets = 10000
else: 
    top_picks = np.zeros((0,63))
    picks_forecast_file = './forecast/fivethirtyeight_ncaa_forecasts.csv'
    # picks_forecast_file = './forecast/5050.csv'
    n_iters = 1000
    Npicks = 50000
    Nbrackets = 1000

for i in range(n_iters):
    picks = search_picks.search(brackets_forecast_file, scoring_type,
        Nbrackets = Nbrackets, Npicks = Npicks, 
        pick_ids_in=top_picks, picks_forecast_file=picks_forecast_file)
    if do_round2:
        search_picks.write_picks(picks)