import pokemon
from poke_utils import *
import subprocess, shlex
from pokemon_statistics import *
import pickle
from model_teams import NeuralNetTeams
import torch
import queue
import random
from watchdog import Watchdog

'''
Todo:
// Update state (history)
Choose pokemon to send out
Parallelize pikalytics to speed up
'''

class simulator:

    ms = None
    movedex = None

    def __init__(self, my_team, oppo_team):
        '''
        my_team: Full team with pokemon, moves, evs, etc.
        oppo_team: Only pokemon names
        '''

        self.ms = state()

        # Parse my_team
        self.ms.team1 = self.parse_my_team(my_team)

        # create parse_oppo_team
        self.ms.team2 = self.parse_oppo_team(oppo_team)

        f = open("movedex.pkl", "rb")
        self.movedex = pickle.load(f)
        f.close()

        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        torch.cuda.empty_cache()

        self.lead_net = NeuralNetTeams(0.01)
        self.lead_net.load_model('sample_model')
        self.lead_net.to(self.device)

        self.output = queue.Queue()


    def get_output(self):
        return self.output


    def findBestMove(self, is_random=False, top_moves=5):

        ms = self.ms
        movedex = self.movedex

        f = open("ms.pkl", "wb")
        pickle.dump(ms, f)
        f.close()

        p1moves = genMoveCombos(ms.team1.active, 'p1', movedex)
        p2moves = genMoveCombos(ms.team2.active, 'p2', movedex)

        if is_random or len(ms.team1.active) == 1 or len(ms.team2.active) == 1:
            return self.randomMove(p1moves)

        p = subprocess.Popen(shlex.split('python3 run_sim.py'))
        try:
            p.wait(timeout=40)
            f = open("best_move.txt", "r")
            best_move = f.readline()
            f.close()
        except subprocess.TimeoutExpired as e:
            # Simulation is taking too long to return, kill and return random
            p.kill()
            return self.randomMove(p1moves)

        # Todo: One pokemon remaining

        move_targets = re.search(r'p1\ move\ (?P<move1>[1-4])(\ )?(?P<target1>(-1|-2|1|2))?\ *(,\ move\ (?P<move2>[1-4])(\ )?(?P<target2>(-1|-2|1|2))?)?', best_move)

        for cmd in move_targets.groupdict().values():
            if cmd:
                self.output.put(str(cmd))

        return move_targets.groupdict().values()

    def randomMove(self, p1moves):
        random_move = random.choice(p1moves)

        move_targets = re.search('p1\ move\ (?P<move1>[1-4])(\ )*(?P<target1>(-1|-2|1|2))?(, move\ (?P<move2>[1-4])(\ )*(?P<target2>(-1|-2|1|2))?)?', random_move)

        for cmd in move_targets.groupdict().values():
            if cmd:
                self.output.put(str(cmd))

        return move_targets.groupdict().values()

    def select_lead(self):
        '''
        Replace with better predictions
        '''
        leads = random.sample(['0', '1', '2', '3', '4', '5'], 4)

        for idx in leads:
            self.output.put(idx)

        return leads


    def select_replacement(self, replace=1):
        '''
        Replace with better predictions
        '''
        # Have to handle dual swap-ins better than just random
        replacements = random.sample(['2', '3'], replace)

        for idx in replacements:
            self.output.put(idx)

        return replacements


    def pred_lead(self):
        team = torch.zeros(979)
        f = open("poke_to_idx.pkl", 'rb')
        poke_to_idx = pickle.load(f)
        f.close()

        indices = []

        for poke in self.ms.team2.full:
            indices.append(poke_to_idx[poke.name])

        for idx in indices:
            team[idx] = 1

        output = self.lead_net(team.float().to(self.device))

        lead_scores = []
        for poke in self.ms.team2.full:
            lead_scores.append((poke.name, output[0, poke_to_idx[poke.name] ]))


        lead_scores.sort(key=lambda x:-x[1][2])

        for i in lead_scores:
            print(i)

        return lead_scores[0][0], lead_scores[1][0]


    def parse_my_team(self, my_team):
        # Todo
        poke_item = re.compile('(?P<pokemon>.+)\ @\ (?P<item>.+)')
        ability = re.compile('Ability:\ (?P<ability>.+)')
        level = re.compile('level:\ (?P<ability>.+)')
        evs = re.compile('EVs:\ ((?P<hp>[0-9]+)\ HP)?((\ \/\ )?(?P<atk>[0-9]+)\ Atk)?((\ \/\ )?(?P<def>[0-9]+)\ Def)?((\ \/\ )?(?P<spa>[0-9]+)\ SpA)?((\ \/\ )?(?P<spd>[0-9]+)\ SpD)?((\ \/\ )?(?P<spe>[0-9]+)\ Spe)?')
        nature = re.compile('(?P<Nature>.+)\ Nature')
        ivs = re.compile('IVs:\ ((?P<hp>[0-9]+)\ HP)?((\ \/\ )?(?P<atk>[0-9]+)\ Atk)?((\ \/\ )?(?P<def>[0-9]+)\ Def)?((\ \/\ )?(?P<spa>[0-9]+)\ SpA)?((\ \/\ )?(?P<spd>[0-9]+)\ SpD)?((\ \/\ )?(?P<spe>[0-9]+)\ Spe)?')
        move = re.compile('\-\ (?P<move>.+)')

        mteam = team()
        mteam.side = 'p1'
        mteam.full = []

        stat_names = ['hp', 'atk', 'def', 'spa', 'spd', 'spe']

        f = open(my_team, 'r')
        lines = f.readlines()
        f.close()

        lines.append('\n')

        for i in range(6):

            line = lines.pop(0)
            match = poke_item.match(line)
            pokename = match.group('pokemon')
            item = match.group('item')

            poke = pokemon(pokename)
            poke_stats = getPikalytics(pokename)

            line = lines.pop(0)
            match = ability.match(line)
            a = match.group('ability')

            line = lines.pop(0)
#             match = level.match(line)
#             item = match.group('level')

            line = lines.pop(0)
            match = evs.match(line)
            for stat in stat_names:
                if match.group(stat) != None:
                    poke_stats[4][0][stat] = int(match.group(stat))
                else:
                    poke_stats[4][0][stat] = 0


            line = lines.pop(0)
            match = nature.match(line)
            n = match.group('Nature')

            line = lines.pop(0)
            match = ivs.match(line)
            for stat in stat_names:
                if match.group(stat) != None:
                    poke.ivs[stat] = int(match.group(stat))
                else:
                    poke.ivs[stat] = 31

            poke.moves = []

            for i in range(4):
                line = lines.pop(0)
                match = move.match(line)
                m = match.group('move').replace(' ', '')
                poke.moves.append(m)

            poke.item = item.replace(' ', '')
            poke.ability = a.replace(' ', '')
            poke_stats[4][0]['nature'] = n.replace(' ', '')

            calcStats(poke, poke_stats)
            updatePred(poke, poke_stats)

            mteam.full.append(poke)

            line = lines.pop(0)


        return mteam


    def parse_oppo_team(self, oppo_team):
        # Todo
        oppo = team()

        oppo.side = 'p2'

        oppo.full = []

        for poke in oppo_team:
            oppo.full.append(createPikalyticsPokemon(poke))

        return oppo


    def my_team_active(self, poke1, poke2=None):
        '''
        poke1      : string of pokemon name
        poke2 (opt): string of pokemon name
        '''
        self.ms.team1.active = []

        self.my_poke_active(poke1, self.ms.team1)

        if poke2 != None:
            self.my_poke_active(poke2, self.ms.team1)


    def oppo_team_active(self, poke1, poke2=None):
        '''
        poke1      : string of pokemon name
        poke2 (opt): string of pokemon name
        '''
        self.ms.team2.active = []

        self.my_poke_active(poke1, self.ms.team2)

        if poke2 != None:
            self.my_poke_active(poke2, self.ms.team2)


    def my_poke_active(self, poke_name, team):

        poke = None
        for p in team.full:
            if p.name == poke_name:
                poke = p
                break
        if poke == None:
            print("Pokemon not found on team:", poke_name)
            return
        team.active.append(poke)


    def parse_battle_history(self, file='battle-history.txt'):


        f = open(file, 'r')

        for line in f:

            opposing = re.search('opposing', line)

            # Opponent pokemon used a move
            # Add to known moves
            match = re.search('The\ opposing\ (?P<poke>.+)\ used\ (?P<move>.+)!', line)
            if match:
                for poke in self.ms.team2.full:
                    if poke.name == match.group('poke'):
                        if match.group('move') not in poke.moves:
                            poke.moves.append(match.group('move'))
                        break
                continue

            # We know our pokemon moves so we dont need above for our side

            # Opponent pokemon lost hp
            match = re.search('The\ opposing\ (?P<poke>.+)\ lost\ (?P<lost_hp>[0-9]+)%\ of\ its\ health!', line)
            if match:
                for poke in self.ms.team2.full:
                    if poke.name == match.group('poke'):
                        poke.hp -= int(poke.stats['hp'] * int(match.group('lost_hp')) )
                        break
                continue

            # Our pokemon lost hp
            match = re.search('(?P<poke>.+)\ lost\ (?P<lost_hp>[0-9\.]+)%\ of\ its\ health!', line)
            if match:
                for poke in self.ms.team1.full:
                    if poke.name == match.group('poke'):
                        poke.hp -= int(poke.stats['hp'] * int(match.group('lost_hp')) )
                        break
                continue

            # Opposing pokemon fainted
            match = re.search('The\ opposing\ (?P<poke>.+)\ fainted!', line)
            if match:
                for poke in self.ms.team2.full:
                    if poke.name == match.group('poke'):
                        poke.faint = 'dead'
                        if poke in self.ms.team2.active:
                            self.ms.team2.fainted = self.ms.team2.active.index(poke) + 1
                            self.ms.team2.active.remove(poke)
                        break
                continue

            # Our pokemon fainted
            match = re.search('(?P<poke>.+)\ fainted!', line)
            if match:
                for poke in self.ms.team1.full:
                    if poke.name == match.group('poke'):
                        poke.faint = 'dead'
                        if poke in self.ms.team1.active:
                            self.ms.team1.fainted = self.ms.team1.active.index(poke) + 1
                            self.ms.team1.active.remove(poke)
                        break
                continue

            # opponent sent out a new pokemon
            match = re.search('(?P<opponent>.+)\ sent\ out\ (?P<poke>.+)!', line)
            if match:
                for poke in self.ms.team2.full:
                    if poke.name == match.group('poke'):
                        if self.ms.team2.fainted == 1:
                            self.ms.team2.active.insert(0, poke)
                        else:
                            self.ms.team2.active.append(poke)
                        break
                continue

            # we sent out a new pokemon
            match = re.search('Go!\ (?P<poke>.+)!', line)
            if match:
                for poke in self.ms.team1.full:
                    if poke.name == match.group('poke'):
                        if self.ms.team1.fainted == 1:
                            self.ms.team1.active.insert(0, poke)
                        else:
                            self.ms.team1.active.append(poke)
                        break
                continue

            # opponent withdrew out a new pokemon
            match = re.search('(?P<opponent>.+)\ withdrew\ (?P<poke>.+)!', line)
            if match:
                for poke in self.ms.team2.active:
                        if poke in self.ms.team2.active:
                            self.ms.team2.fainted = self.ms.team2.active.index(poke) + 1
                            self.ms.team2.active.remove(poke)
                        break
                continue

            # we withdrew a pokemon
            match = re.search('(?P<poke>.+),\ come\ back!', line)
            if match:
                for poke in self.ms.team1.active:
                    if poke.name == match.group('poke'):
                        if poke in self.ms.team1.active:
                            self.ms.team1.fainted = self.ms.team1.active.index(poke) + 1
                            self.ms.team1.active.remove(poke)
                        break
                continue

            match = re.search('frisked', line)
            if match and opposing:
                item = re.search('opposing\ (?P<poke>.+)\ and\ found\ its\ (?P<item>.+)(!)?', line)
                for poke in self.ms.team2.full:
                    if poke.name == item.group('poke'):
                        poke.item = item.group('item')
                        break
                continue

            match = re.search('hung\ on\ using\ its\ ', line)
            if match and opposing:
                match2 = re.search('opposing\ (?P<poke>.+)\ ', line)
                for poke in self.ms.team2.full:
                    if poke.name == poke.group('poke'):
                        poke.item = 'Focus Sash'
                        break
                continue

            match = re.search('restored\ a\ little\ HP\ using\ its\ (?P<item>.+)(!)?', line)
            if match and opposing:
                match2 = re.search('opposing\ (?P<poke>.+)\ ', line)
                for poke in self.ms.team2.full:
                    if poke.name == match2.group('poke'):
                        poke.item = match.group('item')
                        break
                continue

            match = re.search('lost some of its HP', line)
            if match and opposing:
                match2 = re.search('opposing\ (?P<poke>.+)\ ', line)
                for poke in self.ms.team2.full:
                    if poke.name == match2.group('poke'):
                        poke.item = "Life Orb"
                        break
                continue

            match = re.search('is\ about\ to\ be\ attacked\ by\ its\ (?P<item>.+)(!)?', line)
            if match and opposing:
                match2 = re.search('opposing\ (?P<poke>.+)\ ', line)
                for poke in self.ms.team2.full:
                    if poke.name == match2.group('poke'):
                        poke.item = match.group('item')
                        break
                continue

            match = re.search('knocked\ off', line)
            if match and opposing:
                match2 = re.search('opposing\ (?P<poke>.+)\'s\ (?P<item>.+)(!)?', line)
                for poke in self.ms.team2.full:
                    if poke.name == match2.group('poke'):
                        poke.item = match2.group('item')
                        break
                continue

            match = re.search('\ ate\ its\ ', line)
            if match and opposing:
                match2 = re.search('\(The\ opposing\ (?P<poke>.+)\ ate\ its\ (?P<item>.+)!\)', line)
                for poke in self.ms.team2.full:
                    if poke.name == match2.group('poke'):
                        poke.item = match2.group('item')
                        break
                continue

            match = re.search('sent\ out\ ', line)
            if match:
                match2 = re.search('sent\ out\ (?P<poke>.+)(!)?', line)
                self.ms.team2.active.append(match2.group('poke'))
                continue

        f.close()
