import pdb
import urllib.request
import forecast
import yahoo_parsing

def read_from_file(fname):
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
                    picks[i].append(line.strip())
                   
    return picks 
 

class Picks:
    def __init__(self, fname):
        self.name = fname
        teams = []
        if fname[0:4] == 'http':
            self.picks = yahoo_parsing.parse_bracket(fname)
        else:   
            self.picks = read_from_file(fname)
   
    def write_to_file(self, outname):
        with open(outname, 'wt') as f:
            f.write('?\n')
            for rnd in self.picks:
                f.write('-\n')    
                for team in rnd:
                    f.write(team.strip() + '\n')
   
    def convert_to_id(self, forecast):
        pick_ids = [] 
        for rd in self.picks:
            for pick in rd:
                pick_ids.append(forecast.name_to_id(pick))
        return pick_ids
        
