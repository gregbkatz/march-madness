import os
import picks
import yahoo_parsing
import pdb


# d = './family'
# group_id = 44100

d = './spacex'
group_id = 73952

if not os.path.isdir(d):
    os.makedirs(d)

members_table = d + '/members_table'
# yahoo_parsing.parse_group(group_id, members_table)
lpicks = []
names, url_codes = yahoo_parsing.parse_members_table(members_table)
for i in range(0, len(names)):
    url = 'http://tournament.fantasysports.yahoo.com/t1/' + url_codes[i]
    print(url_codes[i] + ' ' + names[i])
    lpicks.append(picks.Picks(url))

for i, pick in enumerate(lpicks):
    pick.write_to_file(os.path.join(d, names[i] + '.picks'))
