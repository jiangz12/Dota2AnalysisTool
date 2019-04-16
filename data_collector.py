'''
Source: https://medium.com/@waprin/python-and-dota2-analyzing-team-liquids-io-success-and-failure-7d44cc5979b2
'''
import json
#import time
import requests
import datetime as dt

TEAM_ID = 15

# selcet the matches from the given time section, for example the version 7.21
start = dt.datetime(1970, 1, 1, 0, 0, 0)
end = dt.datetime(2019, 1, 29, 0, 0, 0)
now = dt.datetime.now()
start_time = (end - start).total_seconds()


h = requests.get('https://api.opendota.com/api/heroes')
heros = h.json()
with open('hero.json', 'w') as outfile:
    json.dump(heros, outfile)
    
t = requests.get('https://api.opendota.com/api/teams')
teams = t.json()
with open('team.json', 'w') as outfile:
    json.dump(teams, outfile)

r = requests.get('http://api.opendota.com/api/teams/' + str(TEAM_ID) + '/matches')
matches = r.json()
with open('match.json', 'w') as outfile:
    total = 0
    selected_matches = []
    for m in matches:
        if m['start_time'] > start_time:
            print('requseting match {}'.format(m['match_id']))
            r = requests.get('https://api.opendota.com/api/matches/{}'.format(m['match_id']))
            match_data = r.json()
            selected_matches.append(match_data)
            total += 1
    json.dump(selected_matches, outfile)

print('Loading {} matches\n'.format(total))
