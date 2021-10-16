import subprocess, shlex
from multiprocessing import Process, Queue, current_process
from pokemon import *
import copy
from sim_parser import outputParser
from heuristics import *
from random import choice
from watchdog import Watchdog

# showdown_cmd = './showdownsimulator/pokemon-showdown/pokemon-showdown simulate-battle'
showdown_cmd = 'node showdownsimulator/pokemon-showdown/pokemon-showdown simulate-battle'

def prin(*args):
    if False:
        print(*args)



def runSimList(state, p1moves, p2moves, side=1, sims_proc=10):
    # state: pokemon on both sides, weather, etc
    # p1moves: moves to test for p1
    # p2moves: moves to test for p2
    # side: which side we're testing
    
    threads = []
    results = Queue()
    
    # start process
    i = 0
    if side == 1:
        for move in p1moves:
            print('\t\t', len(p1moves), end='\r')
            t = Process(target=simWrapperList, args=(results, state, move, p2moves, side, sims_proc))
            t.start()
            threads.append(t)
    else:
        for move in p2moves:
            print('\t\t', len(p2moves), end='\r')
            t = Process(target=simWrapperList, args=(results, state, p1moves, move, side, sims_proc))
            t.start()
            threads.append(t)
    
    # Wait for sim to end
    i = 1
    watchdog = Watchdog(10)
    try:
        while len(threads) > 0:
            for t in threads:
                t.join(0.01)
                if t.exitcode != None:
                    threads.remove(t)
                    print('\t\t\t', i, end='\r')
                    i += 1
    except Exception:
        for t in threads:
            t.terminate()
    watchdog.stop()
    
    scores = []
    # Getting the results
    while not results.empty():
        r = results.get()
        if r == 'Error':
            pass
        else:
            scores.append(r)
    
    scores.sort(key=lambda x:-x[1])
    
    best = max(scores, key=lambda x:x[1])
    
    return scores

        
        
def simWrapperList(q, state, p1moves, p2moves, side, sims_proc=10):
    q.put( repeatSimList(state, p1moves, p2moves, side, sims_proc) )
    print(q.qsize(), end='\r')
                    

        
def repeatSimList(state, p1moves, p2moves, side=1, num_sims=20):
    '''
        Sets up the sim multiple times per process instead of only one
    '''
    
    proc = subprocess.Popen(shlex.split(showdown_cmd), 
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.PIPE, 
                        stdin=subprocess.PIPE, 
                        bufsize=1, 
                        universal_newlines=True)

    
    proc.stdin.write('>start {"formatid":"vgc"}\n')

    team_one = '>player p1 {"name":"Alice","team":"'+ teamToPack(state.team1) + '"}\n'
    team_two = '>player p2 {"name":"Bobby","team":"'+ teamToPack(state.team2) + '"}\n'

    proc.stdin.write(team_one)
    proc.stdin.write(team_two)      
    
    # Select the first two since they are active
    
    proc.stdin.write('>p1 team 1234\n')
    proc.stdin.write('>p2 team 2134\n')
    
    score = 0.0
    result = None

    for i in range(num_sims):
    
        # update to current state

        proc.stdin.write('>p1 reviveAll\n')
        proc.stdin.write('>p2 reviveAll\n')
        
        updateSide(proc.stdin, state.team1)
        updateSide(proc.stdin, state.team2)

        updateField(proc.stdin, state)

        # Run moves

        if side == 1:
            if type(choice(p2moves)) != str:
                p2moves = p2moves[0]
            proc.stdin.write(p1moves)
            proc.stdin.write(choice(p2moves))
            
        else:
            while type(choice(p1moves)) != str:
                p1moves = p1moves[0]
            proc.stdin.write(choice(p1moves))
            proc.stdin.write(p2moves)
            

        newState = copy.deepcopy(state)
        exit_phase = '|upkeep'
        reading = True

        while reading:

            for line in iter(proc.stdout.readline, ''):

                # Parser here with update to state
                result = outputParser(line, newState, result)
                

                if result != None:
                    if result[1] == 'do switch':
                        '''
                            Todo:
                            Switch random pokemon in 
                        '''
                        proc.stdin.write('>p' + result[0] + ' switch 3\n')

                if (exit_phase in line):
                    # Run heuristic here
                    reading = False
                    
                    score += heuristic(state, newState, side)
                    
                    # Check for fainted pokemon and swap and alter

                    faint_count = 0
                    for poke in newState.team1.active:
                        if poke.faint == 'dead':
                            faint_count += 1
                    
                    if faint_count > 0:
                        cmd = ">p1 switch 3"
                        if faint_count == 2:
                            cmd += ', switch 4'
                        cmd += '\n'
                        proc.stdin.write(cmd)
                    
                    faint_count = 0
                    for poke in newState.team2.active:
                        if poke.faint == 'dead':
                            faint_count += 1
                    
                    if faint_count > 0:
                        cmd = ">p2 switch 3"
                        if faint_count == 2:
                            cmd += ', switch 4'
                        cmd += '\n'
                        proc.stdin.write(cmd)
                    break
                            


                if ('|error|' in line):
                    proc.kill()
                    g = open('outputs/error' + str(current_process()._name) + '.txt', 'w')
                    g.write(line)
                    g.close()
                    proc.kill()
                    if side == 1 and i > 0:
                        return (p1moves, score / i)
                    elif side == 2 and i > 0:
                        return (p2moves, score / i)
                    elif side == 1:
                        return 'Error'
                    else:
                        return 'Error'
                
    proc.kill()
    if side == 1:
        return (p1moves, score / num_sims)
    else:
        return (p2moves, score / num_sims)



def updateField(proc_input, state):
    
    weather = '>p1 weather ' + state.weather + ' \n'
    proc_input.write(weather)
    
    terrain = '>p1 terrain ' + state.terrain + ' \n'
    proc_input.write(terrain)
    
    for pweather in state.pseudoweather:
        pseudoweather = '>p1 pseudoweather ' + pweather + ' \n'
        proc_input.write(pseudoweather)
        prin(pseudoweather)
        
        
        
def updateSide(proc_input, myTeam):
    
    stat_names = ['hp', 'atk', 'def', 'spa', 'spd', 'spe']
    boosts_names = ['atk', 'def', 'spa', 'spd', 'spe', 'accuracy', 'evasion']
    base = '>' + myTeam.side + ' '
    
    alive_cmd = base
    for poke in myTeam.active:
        alive_cmd += 'fainted ' + poke.faint + ', '
    alive_cmd = alive_cmd[:-2] + ' \n'
    
    proc_input.write(alive_cmd)
    prin(alive_cmd)
    
    
    
    stat_cmd = base
    for poke in myTeam.active:
        stat_cmd += 'stats '
        for stat in stat_names:
            stat_cmd += str(poke.stats[stat]) + ' '
        stat_cmd += ', '
    stat_cmd = stat_cmd[:-2] + ' \n'
    
    proc_input.write(stat_cmd)
    prin(stat_cmd)
    
    
    hp_cmd = base
    for poke in myTeam.active:
        hp_cmd += 'hp ' + str(poke.hp)
        hp_cmd += ', '
    hp_cmd = hp_cmd[:-2] + ' \n'
    
    proc_input.write(hp_cmd)
    prin(hp_cmd)
    
    
    boost_cmd = base
    for poke in myTeam.active:
        boost_cmd += 'boosts '
        for boost in boosts_names:
            boost_cmd += str(poke.boosts[boost]) + ' '
        boost_cmd += ', '
    boost_cmd = boost_cmd[:-2] + ' \n'
    
    proc_input.write(boost_cmd)
    prin(boost_cmd)
    
    
    move_cmd = base
    for poke in myTeam.active:
        move_cmd += 'moves '
        for move in poke.moves:
            move_cmd += move + ' '
        for i in range(4 - len(poke.moves)):
            move_cmd += poke.pred_moves[i] + ' '
        move_cmd += ', '
    move_cmd = move_cmd[:-2] + ' \n'
    
    proc_input.write(move_cmd)
    prin(move_cmd)
    
    
    ability_cmd = base
    for poke in myTeam.active:
        if (poke.ability == ' ' or poke.ability == ''):
            ability_cmd += 'ability ' + poke.pred_ability
        else:
            ability_cmd += 'ability ' + poke.ability
        ability_cmd += ', '
    ability_cmd = ability_cmd[:-2] + ' \n'
    
    proc_input.write(ability_cmd)
    prin(ability_cmd)
    
    
    item_cmd = base
    for poke in myTeam.active:
        if (poke.item == ' ' or poke.item == ''):
            item_cmd += 'item ' + poke.pred_item
        else:
            item_cmd += 'item ' + poke.item
        item_cmd += ', '
    item_cmd = item_cmd[:-2] + ' \n'
    
    proc_input.write(item_cmd)
    prin(item_cmd)
    
    
    status_cmd = base
    for poke in myTeam.active:
        status_cmd += 'status ' + pokemon.status
        status_cmd += ', '
    status_cmd = status_cmd[:-2] + ' \n'
    
    proc_input.write(status_cmd)
    prin(status_cmd)
    
    
    types_cmd = base
    for poke in myTeam.active:
        types_cmd += 'types '
        for t in poke.typing:
            types_cmd += t + ' '
        types_cmd += ', '
    types_cmd = types_cmd[:-2] + ' \n'
    
    proc_input.write(types_cmd)
    prin(types_cmd)
    
    
    protect_cmd = base
    for poke in myTeam.active:
        protect_cmd += 'protected ' + str(pokemon.protected)
        protect_cmd += ', '
    protect_cmd = protect_cmd[:-2] + ' \n'
    
    proc_input.write(protect_cmd)
    prin(protect_cmd)
    
    
    first_cmd = base
    for poke in myTeam.active:
        first_cmd += 'firstTurn ' + str(pokemon.first_turn)
        first_cmd += ', '
    first_cmd = first_cmd[:-2] + ' \n'
    
    proc_input.write(first_cmd)
    prin(first_cmd)
    
    
    for condition in myTeam.side_conditions:
        condition_cmd = base
        condition_cmd += 'sidecondition ' + condition + ' \n'
        proc_input.write(condition_cmd)
        prin(condition_cmd)



def teamToPack(myTeam):
    '''
        pokemon||item|ability|move1,move2,move3,move4|nature|evs||ivs||lvl|] 
        
        Reminder: remove aquare bracket if last
    '''
    stat_names = ['hp', 'atk', 'def', 'spa', 'spd', 'spe']
    
    packedFormat = ''
    
    for pokemon in myTeam.active:
        packedFormat += pokemonToPack(pokemon)
    
    for pokemon in myTeam.full:
        if not pokemon in myTeam.active:
            packedFormat += pokemonToPack(pokemon)
       
    packedFormat = packedFormat[:-1]
    
    return packedFormat



def pokemonToPack(pokemon):
    '''
        pokemon||item|ability|move1,move2,move3,move4|nature|evs||ivs||lvl|]
    '''
    
    stat_names = ['hp', 'atk', 'def', 'spa', 'spd', 'spe']
    
    packedFormat = pokemon.name + '||'
    
    if pokemon.item == '' or pokemon.item == ' ':
        packedFormat += pokemon.pred_item + '|'
    else:
        packedFormat += pokemon.item + '|'

    if pokemon.ability == '' or pokemon.ability == ' ':
        packedFormat += pokemon.pred_ability + '|'
    else:
        packedFormat += pokemon.ability + '|'

    for move in pokemon.moves:
        packedFormat += move + ','
    for i in range(4 - len(pokemon.moves)):
        packedFormat += pokemon.pred_moves[i] + ','
    packedFormat = packedFormat[:-1] + '|'

    packedFormat += pokemon.nature + '|'

    for stat in stat_names:
        packedFormat += str(pokemon.evs[stat]) + ','
    packedFormat = packedFormat[:-1] + '||'

    for stat in stat_names:
        packedFormat += str(pokemon.ivs[stat]) + ','
    packedFormat = packedFormat[:-1] + '||50|]'
    
    return packedFormat
