'''
Source: https://medium.com/@waprin/python-and-dota2-analyzing-team-liquids-io-success-and-failure-7d44cc5979b2
'''
import json
from collections import defaultdict, OrderedDict
from operator import itemgetter
from itertools import chain

TEAM_ID = 15
RADIANT = 0
DIRE = 1
TARGET = None
#TARGET = 'Ember Spirit'


class Match:
    def __init__(self, match_id: int, side: int, is_win: bool):
        ''' side can only be 0 or 1. 0 for radiant, 1 for dire.
        '''
        self.match_id = match_id
        self.side = side
        self.is_win = is_win
        self.picks = []
        self.bans = []
        self.opponent_picks = []
        self.opponent_bans = []


class Hero_collector:
    def __init__(self, matches: [Match]):
        self.matches = matches
        self.hero_wins = defaultdict(int)
        self.hero_totals = defaultdict(int)
        self.hero_side = defaultdict(int)
        self.hero_matches = defaultdict(list)
        self.win_percent = defaultdict(float)
    
    def collect_hero_data(self, is_opponent):
        for match in self.matches:
            picks = match.opponent_picks if is_opponent else match.picks
            for hero in picks:
                self.hero_totals[hero] += 1
                if (is_opponent and not match.is_win) or \
                   (not is_opponent and match.is_win):
                    self.hero_wins[hero] += 1
                    if match.side == RADIANT:
                        self.hero_side[hero] += 1
                self.hero_matches[hero].append(match.match_id)

        for k, v in self.hero_wins.items():
            self.win_percent[k] = (v / self.hero_totals[k])

    def get_sorted_win_rate_dict(self):
        return OrderedDict(sorted(self.win_percent.items(), 
                                              key=itemgetter(1), reverse=True))
    
    def get_sorted_win_rate_and_matches_dict(self):
        merged = defaultdict(list)
        for k, v in chain(self.win_percent.items(), self.hero_wins.items()):
            merged[k].append(v)
        return sorted(merged.items(), key=itemgetter(1), reverse=True)
    
    def highest_win_rate_hero(self):
        return self.get_sorted_win_rate_and_matches_dict()[0][0]
    
    def lowest_win_rate_hero(self):
        return self.get_sorted_win_rate_and_matches_dict()[-1][0]


# create a dictionary of hero names
names = {}
with open('hero.json') as f:
    data = json.load(f)
    for h in data:
        names[h['id']] = h['localized_name']


def process_match(match):
    if match['radiant_team']['team_id'] == TEAM_ID:
        side = RADIANT
    else:
        side = DIRE

    if side == RADIANT:
        is_win = match['radiant_win']
    else:
        is_win = not match['radiant_win']

    m = Match(match['match_id'], side, is_win)

    for pb in match['picks_bans']:
        if pb['team'] == side and pb['is_pick']:
            m.picks.append(names[pb['hero_id']])
        if pb['team'] == side and not pb['is_pick']:
            m.bans.append(names[pb['hero_id']])
        if pb['team'] != side and pb['is_pick']:
            m.opponent_picks.append(names[pb['hero_id']])
        if pb['team'] != side and not pb['is_pick']:
            m.opponent_bans.append(names[pb['hero_id']])
    return m


with open('match.json') as f:
    matches = json.load(f)

processed = 0
errors = 0
processed_matches = []
for match in matches:
    try:
        processed_matches.append(process_match(match))
        processed += 1
    except Exception as e:
        errors += 1

print("Processed {} Errors {}".format(processed, errors))


won_matches = list(filter(lambda m : m.is_win, processed_matches))
print('The team won {} of the games.'.format(len(won_matches)))


if TARGET is None:
    hc = Hero_collector(processed_matches)
    hc.collect_hero_data(False)
    TARGET = hc.lowest_win_rate_hero()
print('{} is the target.'.format(TARGET))


target_banned = list(filter(lambda m: TARGET in m.opponent_bans, processed_matches))
target_matches = list(filter(lambda m: TARGET in m.picks, processed_matches))
print(TARGET + ' was banned in {} matches.'.format(len(target_banned)))
print('Found {} out of {} games where the team picked '.format(len(target_matches), 
        len(processed_matches) - len(target_banned)) + TARGET + ' without been banned.')


target_lost_matches = filter(lambda m: not m.is_win, target_matches)
print(TARGET + ' lost {} out of {} games.'.format(len(list(target_lost_matches)), 
                                                  len(target_matches)))



print('------------Opponents---------------------')
oc = Hero_collector(target_matches)
oc.collect_hero_data(True)
sorted_percent = oc.get_sorted_win_rate_dict()

for k, v in sorted_percent.items():
    print('Hero {} has won {} out of {} games against '.format(k, oc.hero_wins[k], oc.hero_totals[k]) + TARGET + 
          ' for a win percent of {} ({} matches were at Radiant)'.format(v, oc.hero_side[k]))
