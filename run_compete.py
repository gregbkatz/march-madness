import os
import compete
import pdb
import picks
import forecast
import random 
random.seed(0)

# def __init__(self, d, ncases, forecast_file, truth_file, source, use_bonus):

# d = 'family'
d = 'spacex'

forecast_file = './forecast/fivethirtyeight_ncaa_forecasts.csv'
# forecast_file = './forecast/5050.csv'
# truth_file = ''
# truth_file = 'rd1.truth'
truth_file = 'rd2.truth'
# truth_file = 'scenario.truth'
ncases = 1000

pcks = []
names = []
for file in os.listdir(d):
    if file.endswith(".picks"):
        pcks.append(picks.Picks(os.path.join(d, file)))
        names.append(file)

forecast = forecast.Forecast(forecast_file, truth_file)
forecast.write_truth_file('base.truth')
mcc = compete.Compete(pcks, forecast, d)
mcc.run_MC(ncases)

print(forecast.forecast_file)
print(forecast.truth_file)
print(mcc.ncases)
print('{:30},{:10},{:10},{:10},{:10},{:10},{:10}'.format(
	'Bracket Name', 'min score', 'max score', 'P lose', 'P win', 'min rank', 'max rank'))
#  self.mcc.curr_order = [7,13,10,2,9,5,12,4,1,11,8,12,3,0,6]
#  self.mcc.curr_order = range(0,14)]
# for i in mcc.curr_order:
for i in range(0,len(names)):
    print('{:30},{:10.0f},{:10.0f},{:10.1f},{:10.1f},{:10.0f},{:10.0f}'.format(
    	names[i], mcc.min_scores[i], mcc.max_scores[i], mcc.plose[i]*100, mcc.pwin[i]*100, 
    	mcc.worst_finish[i], mcc.best_finish[i]))



