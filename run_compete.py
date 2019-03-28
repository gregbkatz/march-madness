from compete import Compete
import pdb
import forecast
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
mcc = Compete(picks_dir, forecast_file, truth_file, bonus_type)
mcc.run_MC(10000)
mcc.summary()

