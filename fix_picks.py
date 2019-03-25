import csv
import pdb
import copy
import os

def read_picks(fname):
    picks = []
    i = -1
    initialized = False
    with open(fname, 'r') as f:
        for line in f:
            if not initialized and line[0] == '-':
                initialized = True
            if initialized:
                if line[0] == '-':
                    picks.append([])
                    i += 1
                else:
                    words = line.split()
                    #picks[i].append(' '.join(words[2:]))
                    picks[i].append(line.strip())
    return picks

def write_picks(picks, outname):
    with open(outname, 'wt') as f:
        f.write('?\n')
        for rnd in picks:
            f.write('-\n')    
            for team in rnd:
                f.write(team.strip() + '\n')

def fix(fname):
    picks = read_picks(fname)

    picks2 = copy.deepcopy(picks)
    picks2[0][8:16] = copy.deepcopy(picks[0][16:24])
    picks2[0][16:24] = copy.deepcopy(picks[0][8:16])

    picks2[1][4:8] = copy.deepcopy(picks[1][8:12])
    picks2[1][8:12] = copy.deepcopy(picks[1][4:8])

    picks2[2][2:4] = copy.deepcopy(picks[2][4:6])
    picks2[2][4:6] = copy.deepcopy(picks[2][2:4])

    # picks2[3][1] = copy.deepcopy(picks[3][2])
    # picks2[3][2] = copy.deepcopy(picks[3][1])

    write_picks(picks2, fname)

# d = './spacex/'
d = './family/'
for file in os.listdir(d):
    if file.endswith(".picks"):
        print(file)
        fix(d + file)

