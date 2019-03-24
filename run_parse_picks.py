import os
import picks
import pdb


# d = './family'
# group_id = 44100

d = './spacex'

members_table = d + '/members_table'
# picks.parse_yahoo_group(group_id, members_table)
lpicks = []
names, url_codes = picks.parse_members_table(members_table)
for i in range(0, len(names)):
    url = 'http://tournament.fantasysports.yahoo.com/t1/' + url_codes[i]
    print(url_codes[i] + ' ' + names[i])
    lpicks.append(picks.Picks(url))

if not os.path.isdir(d):
    os.makedirs(d)

for i, pick in enumerate(lpicks):
    pick.write_picks(os.path.join(d, names[i] + '.picks'))
