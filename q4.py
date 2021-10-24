import sys
import json


def dictTrans(DFA):
    transDict = {}

    for transition in DFA["transition_function"]:
        transDict[(transition[0], transition[1])] = transition[2]

    return transDict


def createDead(DFA, states, transDict):
    deadState = "DEAD"
    states.append(deadState)
    for letter in DFA["letters"]:
        transDict[(deadState, letter)] = deadState
    
    for state in states:
        for letter in DFA["letters"]:
            if (state, letter) not in transDict.keys():
                transDict[(state, letter)] = deadState

    return states, transDict


def startPart(DFA, states):
    accPart = DFA["final_states"]
    nonaccPart = [] 
    
    for state in states:
        if  state not in accPart:
            nonaccPart.append(state)
    
    return [accPart, nonaccPart]


def compPart(DFA, transDict, partitions, first, second):
    for letter in DFA["letters"]:
        endFirst = transDict[(first, letter)]
        endSecond = transDict[(second, letter)]

        indexFirst = [partitions.index(partition) for partition in partitions if endFirst in partition][0]
        indexSecond = [partitions.index(partition) for partition in partitions if endSecond in partition][0]

    return (indexFirst == indexSecond)

def unionGroups(first, second, groups):
    groupFirst = [group for group in groups if first in group][0]
    groupSecond = [group for group in groups if second in group][0]

    if groupFirst != groupSecond:
        groups.remove(groupFirst)
        groups.remove(groupSecond)
        groups = groups + [groupFirst + groupSecond]
        
    return groups


def getPart(DFA, transDict, partition, partitions):
        groups = []
        for state in partition:
            groups.append([state])
        
        for i in range(len(partition)):
            for j in range(i+1, len(partition)):
                isTrue = compPart(DFA, transDict, partitions, partition[i], partition[j])
                if isTrue:
                    groups = unionGroups(partition[i], partition[j], groups)
        
        return groups


def makePart(DFA, transDict, partitions):
    newPart = []
    for partition in partitions:
        groups = getPart(DFA, transDict, partition, partitions)
        for i in groups:
            newPart.append(i)
    
    if sorted([sorted(partition) for partition in partitions]) != sorted([sorted(partition) for partition in newPart]):
        partitions = makePart(DFA, transDict, newPart)
    
    return partitions


def buryDead(states, partitions, transDict):
    deadState = "DEAD"

    index = [partitions.index(partition) for partition in partitions if deadState in partition][0]
    p = partitions[index]

    if len(p) != 1:
        partitions[index].remove(deadState)
    else:
        partitions.remove(p)

    states.remove(deadState)

    transitions = transDict.copy()
    for key, value in transitions.items():
        if value == deadState:
            transDict.pop(key)
    
    return states, partitions, transDict

def makeTrans(transDict, partitions):
    transitions = []

    for key,value in transDict.items():
        state1, letter, state2 = key[0], key[1], value
        newState1 = [part for part in partitions if state1 in part][0]
        newState2 = [part for part in partitions if state2 in part][0]
        
        newTrans = [newState1, letter, newState2]
        
        if newTrans not in transitions:
            transitions.append(newTrans)
    
    return transitions

def minimiseDFA(DFA):
    states = DFA["states"]
    transDict = dictTrans(DFA)

    states, transDict = createDead(DFA, states, transDict)
    partitions = startPart(DFA, states)
    partitions = makePart(DFA, transDict, partitions)
    states, partitions, transDict = buryDead(states, partitions, transDict)

    
    letters = DFA["letters"]
    start_states = [state for state in partitions if DFA["start_states"][0] in state]
    final_states = [state for state in partitions if len(set(state) & set(DFA["final_states"]))]

    minDFA = {
        "states": partitions,
        "letters": DFA["letters"],
        "transition_matrix": makeTrans(transDict, partitions),
        "start_states": [state for state in partitions if DFA["start_states"][0] in state],
        "final_states": [state for state in partitions if len(set(state) & set(DFA["final_states"]))]
    }

    return minDFA


if __name__ == "__main__":
    inFile = sys.argv[1]
    outFile = sys.argv[2]

    with open(inFile, 'r') as readFile:
        DFA = json.load(readFile)

    minDFA = minimiseDFA(DFA) 

    with open(outFile, "w") as writeFile:
        json.dump(minDFA, writeFile)