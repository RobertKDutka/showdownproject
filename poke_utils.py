from pokemon import *

def genMoveCombos(pokes, side, movedex, hitAlly=False):
    '''
    Todo: Only one active pokemon
    
    '''
    
    poke1 = pokes[0]
    poke2 = pokes[1]
    
    base = ">" + side
    combos = []
    
    p1 = poke1.moves + poke1.pred_moves[:4 - len(poke1.moves)]
    p2 = poke2.moves + poke2.pred_moves[:4 - len(poke2.moves)]
    
    moves1 = []
    moves2 = []
    
    for m1 in p1:
        moves1.append(targetChoices(m1, ' -2', movedex, hitAlly))
        
    for m2 in p2:
        moves2.append(targetChoices(m2, ' -1', movedex, hitAlly))
        
    for i1 in range(len(p1)):
        m1 = base + ' move ' + str(i1 + 1)
        for t1 in moves1[i1]:
            m2 = m1 + t1
            for i2 in range(len(p2)):
                m3 = m2 + ', move ' + str(i2 + 1)
                for t2 in moves2[i2]:
                    m4 = m3 + t2 + '\n'
                    combos.append(m4)

    return combos
                    
    
def targetChoices(move, ally, movedex, hitAlly=False):
    v = movedex[move.lower()]
    
    if v == 'adjacentAlly':
        return [ally]
    if v == 'adjacentAllyOrSelf':
        return ['-1', '-2']
    if v == 'adjacentFoe':
        return [' 1', ' 2']
    if v == 'all':
        return ['  ']
    if v == 'allAdjacent':
        return ['  ']
    if v == 'allAdjacentFoes':
        return ['  ']
    if v == 'allies':
        return ['  ']
    if v == 'allySide':
        return ['  ']
    if v == 'allyTeam':
        return ['  ']
    if v == 'any':
        if hitAlly:
            return [ally, ' 1', ' 2']
        else:
            return [' 1', ' 2']
    if v == 'foeSide':
        return ['  ']
    if v == 'normal':
        if hitAlly:
            return [ally, ' 1', ' 2']
        else:
            return [' 1', ' 2']
    if v == 'randomNormal':
        return ['  ']
    if v == 'scripted':
        return ['  ']
    if v == 'self':
        return ['  ']
        
        
        