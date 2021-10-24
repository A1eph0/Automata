import sys
import json
from itertools import combinations as comb


def genStates(NFA):
    states = []
    final_states = []

    for i in range(len(NFA["states"])+1):
        tempList = list(map(list, comb(NFA["states"], i)))
        states = states + tempList
    
    for i in NFA["final_states"]:
        for j in states:
            if (i in j) and (j not in final_states):
                final_states.append(j)
    
    return states, final_states


def preproTrans(NFA):
    transDict = {}

    for state in NFA["states"]:
        for letter in NFA["letters"]:
            transDict[(state, letter)] = set()

    for transition in NFA["transition_function"]:
        transDict[(transition[0], transition[1])].add(transition[2])

    return transDict, []


def genTrans(NFA, states):
    transDict, transition_matrix = preproTrans(NFA)

    for i in states:
        for letter in NFA["letters"]:
            temp = set()
            
            for state in i:
                temp |= transDict[(state, letter)]
            
            transition_matrix.append([i, letter, list(temp)])
    
    return transition_matrix


if __name__ == "__main__":
    inFile = sys.argv[1]
    outFile = sys.argv[2]

    with open(inFile, 'r') as readFile:
        NFA = json.load(readFile)
    
    states, final_states = genStates(NFA)

    DFA = {
        "states": states,
        "letters": NFA["letters"],
        "transition_function": genTrans(NFA, states),
        "start_states": NFA["start_states"],
        "final_states": final_states
    }

    with open(outFile, "w") as writeFile:
        json.dump(DFA, writeFile)