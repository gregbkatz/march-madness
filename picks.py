import pdb
import urllib.request
import forecast

def yahoo_html_region(picks):
    return [picks[0:8], picks[8:12], picks[12:14]]

def yahoo_sort_teams(teams):
    # South = yahoo_html_region(teams[0:])
    # West = yahoo_html_region(teams[14:])
    # East  = yahoo_html_region(teams[35:])
    # Midwest = yahoo_html_region(teams[49:])
    East = yahoo_html_region(teams[0:])
    West = yahoo_html_region(teams[14:])
    South  = yahoo_html_region(teams[28:])
    Midwest = yahoo_html_region(teams[42:])

    x = []
    for i in range(len(South)):
        x.append(East[i] + West[i] + South[i] + Midwest[i])
    x.append(teams[56:60]) # Final Four
    x.append(teams[60:62]) # Finals
    x.append(teams[62:63]) # Champion
    return x

def yahoo_parse_line(line):
    a = line.split('user-pick">')
    b = a[1].split('</em>')
    c = b[1].split('</b>')
    return c[0]

def parse_yahoo_group(group, fname):
    url = 'https://tournament.fantasysports.yahoo.com/t1/group/' + str(group)
    response = urllib.request.urlopen(url)
    f = open(fname, 'wt')
    for linebyte in response:
        line = str(linebyte)
        if line.find('members_table') > 0:
            f.write(line + '\n')
    f.close()

def fix_name(name):
    name = name[0].upper() + name[1:]
    name = name.split(' ')[0]
    return name

def parse_members_table(fname):
    with open(fname, 'r') as f:
        s = f.readline()
        a = s.split('href')
        names = []
        urls = []
        renames = member_renames()
        for entry in a:
            if entry[0:16] == '="https://profil':
                d = entry.split('>')
                name = d[1][0:-3]
                name = fix_name(name)
                if name in renames:
                    name = renames[name]
                names.append(name)
            if entry[0:6] == '="/t1/':
                b = entry.split('>')
                c = b[0].split('"')
                url = c[1][4:]
                urls.append(url)
    return (names, urls)

def member_renames():
    return {"Gregory": "Greg", 
            "Raj arshi": "Raj",
            "Andrew": "Drew",
            "mark Van de": "Mark",
            "duncanm": "Duncan",
            "Nicholas Galano": "Nick"}   

class Picks:
    def __init__(self, fname):
        teams = []
        if fname[0:4] == 'http':
            response = urllib.request.urlopen(fname)
            for linebyte in response:
                line = str(linebyte)
                if line.find('user-pick') > 0:
                    if line.find('Real Winner') == -1 and line.find('None') == -1:
                        teams.append(yahoo_parse_line(line)) 
            picks = yahoo_sort_teams(teams)
            self.picks = picks
            self.teams = teams

        else:   
            # if alt:
            self.read_picks_alt(fname)
            # else:
                # self.read_picks(fname)
   
    def write_picks(self, outname):
        with open(outname, 'wt') as f:
            f.write('?\n')
            for rnd in self.picks:
                f.write('-\n')    
                for team in rnd:
                    f.write(team.strip() + '\n')
   
    def read_picks_alt(self,fname):
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
                       
        self.picks = picks 
 
    # def read_picks(self,fname):
    #     picks = []
    #     with open(fname, 'r') as f:
    #         reader = csv.reader(f)
    #         header = []
    #         for row in reader:
    #             if not header:
    #                 header = row
    #                 for col in header:
    #                     picks.append([])
    #             else:
    #                 i = 0
    #                 for col in row:
    #                     if col:
    #                         picks[i].append(col)
    #                     i += 1
    #     self.picks = picks
        




