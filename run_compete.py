from compete import Compete
import pdb
from forecast import Forecast
import glob
import yahoo_parsing
from picks import Picks
import numpy as np
import random 
random.seed(0)

picks_dir = 'family'
# picks_dir = 'spacex'

forecast_file = './forecast/fivethirtyeight_ncaa_forecasts.csv'
# forecast_file = './forecast/5050.csv'

# truth_file = ''
# truth_file = './truth/rd1.truth'
truth_file = './truth/rd2.truth'
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

mcc = Compete(pick_ids, forecast, bonus_type, names)
mcc.run_MC(10000)
mcc.summary()

