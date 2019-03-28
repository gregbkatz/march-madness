import urllib.request
import os
import picks
import pdb

def run_yahoo_parsing(picks_dir):
    if not os.path.isdir(picks_dir):
        os.makedirs(picks_dir)

    members_table = picks_dir + '/members_table'
    if not os.path.isfile(members_table):
        if picks_dir == 'spacex':
            # For some reason parse_group is not working for spacex
            # group. Solution is to copy and paste the members_table
            # directly by using "view sorce" in chrome
            group_id = 73952
        elif picks_dir == 'family':
            group_id = 44100
        else:
            raise('Unspecified group_id')

        parse_group(group_id, members_table)

    names, url_codes = parse_members_table(members_table)
    picks_list = []
    for i, name in enumerate(names):
        url = 'http://tournament.fantasysports.yahoo.com/t1/' + url_codes[i]
        print(url_codes[i] + ' ' + name)
        fname = os.path.join(picks_dir, name + '.picks')
        picks_list.append(picks.Picks(fname, url=url))

    return picks_list

def parse_bracket(fname):
    teams = []
    response = urllib.request.urlopen(fname)
    for linebyte in response:
        line = str(linebyte)
        if line.find('user-pick') > 0:
            if line.find('Real Winner') == -1 and line.find('None') == -1:
                teams.append(parse_line(line)) 
    teams = sort_teams(teams)
    return teams

def html_region(picks):
    return [picks[0:8], picks[8:12], picks[12:14]]

def sort_teams(teams):
    # Double-check this ordering
    East =    html_region(teams[0:])
    South =    html_region(teams[14:])
    West  =  html_region(teams[28:])
    Midwest = html_region(teams[42:])

    x = []
    for i in range(len(South)):
        # Order should be from website 
        x.append(East[i] + West[i] + South[i] + Midwest[i])
    x.append(teams[56:60]) # Final Four
    x.append(teams[60:62]) # Finals
    x.append(teams[62:63]) # Champion
    return x

def parse_line(line):
    a = line.split('user-pick">')
    b = a[1].split('</em>')
    c = b[1].split('</b>')
    return c[0]

def parse_group(group, fname):
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