import pickle
from simulator import runSimList
from poke_utils import genMoveCombos
import random
import pokemon


if __name__ == "__main__":
        
    f = open("movedex.pkl", "rb")
    movedex = pickle.load(f)
    f.close()
        
    f = open("ms.pkl", "rb")
    ms = pickle.load(f)
    f.close()

    p1moves = genMoveCombos(ms.team1.active, 'p1', movedex)
    p2moves = genMoveCombos(ms.team2.active, 'p2', movedex)

    print('  \t', 1, end='\r')

    round1 = runSimList(ms, p1moves, p2moves, side=1, sims_proc=30)
    p1best = [x[0] for x in round1[:5]]

    print('  \t', 2, end='\r')
    
    f = open("best_move.txt", "w")
    f.write(p1best[0])
    f.close()

    round2 = runSimList(ms, p1best, p2moves, side=2, sims_proc=30)
    p2best = [x[0] for x in round2[:5]]

    print('  \t', 3, end='\r')

    round3 = runSimList(ms, p1moves, p2best, side=1, sims_proc=30)
    final_moves = [x[0] for x in round3[:5]]

    best_move = final_moves[0]

    print('=============', best_move, end='')

    f = open("best_move.txt", "w")
    f.write(best_move)
    f.close()
