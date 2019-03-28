import numpy as np
from forecast import Forecast
from compete import Compete
import pdb
import time
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from scipy.stats import rankdata 

brackets_fname = "./search_picks/brackets.txt"

def summary(picks):
    forecast = Forecast('./forecast/fivethirtyeight_ncaa_forecasts.csv')
    n = 32
    i = 0
    for pick in picks:
        print(forecast.teams[pick].summary())
        i += 1
        if i == n:
            print('------------')
            n = n/2
            i = 0

def plot_i(i, picks, total, avg, perc95, top5_cnt, name, write_to_file):
    if write_to_file:
        with open(brackets_fname, 'at') as f:
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
    with open(brackets_fname) as fp:
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

def search(brackets_forecast_file, scoring_type, Nbrackets=10000, 
        Npicks=10000, pick_ids_in = np.zeros((0,63)), 
        picks_forecast_file = '5050.csv'):

    brackets_forecast = Forecast(brackets_forecast_file)

    picks_forecast = Forecast(picks_forecast_file)
    pick_ids, _ = picks_forecast.gen_brackets(Npicks, use_pickle=False)
    pick_ids = np.vstack((pick_ids, pick_ids_in))
    # picks = np.vstack((picks, baseline))

    mcc = Compete(pick_ids, brackets_forecast, scoring_type)
    t1 = time.time()
    mcc.run_MC(Nbrackets)
    total = mcc.scores
    print('time to score:', time.time() - t1)

    avg = total.mean(axis=0)
    perc95 = np.percentile(total, 95, axis=0)
    ranks = np.zeros_like(total)
    for i in range(total.shape[0]):
        ranks[i,:] = rankdata(total[i,:])
    top5 = ranks > 0.95*(Npicks)
    top5_cnt = top5.sum(axis=0)/Nbrackets
    i1 = avg.argmax()
    i2 = perc95.argmax()
    i3 = top5_cnt.argmax()

    print('{:>6s} {:>6s} {:>6s} {:>6s}'.format('idx', 'mean', '95%', 'top5%'))
    plot_i(i1, pick_ids, total, avg, perc95, top5_cnt, 'max mean', True)
    plot_i(i2, pick_ids, total, avg, perc95, top5_cnt, 'max 95 percentile', i2 != i1)
    plot_i(i3, pick_ids, total, avg, perc95, top5_cnt, 'most top 5%', i3 != i2 and i3 != i1)
    plt.legend()

    # plt.show()
    # pdb.set_trace()
    return pick_ids[i1,:]




