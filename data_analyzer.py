'''
Source: https://medium.com/@waprin/python-and-dota2-analyzing-team-liquids-io-success-and-failure-7d44cc5979b2
'''
import json

TEAM_ID = 15
RADIANT = 0
DIRE = 1
Target = 'Ember Spirit'

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

target_banned = list(filter(lambda m: Target in m.opponent_bans, processed_matches))
target_matches = list(filter(lambda m: Target in m.picks, processed_matches))

print(Target + ' was banned in {} matches.'.format(len(target_banned)))
print('Found {} out of {} games where the team picked '.format(len(target_matches), 
        len(processed_matches) - len(target_banned)) + Target + ' without been banned.')


morph_lost_matches = filter(lambda m: not m.is_win, target_matches)

print(Target + ' lost in {} out of {} games.'.format(len(list(morph_lost_matches)), len(target_matches)))

'''
print('------------Opponents---------------------')
hero_wins = collections.defaultdict(int)
hero_totals = collections.defaultdict(int)
hero_matches = collections.defaultdict(list)
for match in wisp_matches:
    for hero in match.opponent_picks:
        hero_totals[hero] += 1
        if not match.liquid_win:
            hero_wins[hero] += 1
        hero_matches[hero].append(match.match)

win_percent = collections.defaultdict(float)
for k, v in hero_wins.items():
    win_percent[k] = (v/hero_totals[k])

sorted_percent = collections.OrderedDict(sorted(win_percent.items(), key=itemgetter(1), reverse=True))

for k, v in sorted_percent.items():
    print('Hero {} has won {} out of {} games against Liquid IO for a win percent of {} (matches {})'.format(
        k, hero_wins[k], hero_totals[k], v, hero_matches[k]))
'''
