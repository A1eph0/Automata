import sys 
import json


def removeState(state, transition_matrix, states):
    selfList = []
    fromList = []
    toList = []

    for i in states:
        tempFrom = set()
        tempTo = set()

        newTrans = []

        for transition in transition_matrix:
            if transition[0] == state and transition[2] == i:
                tempFrom.add(transition[1])
                
            elif transition[0] == i and transition[2] == state:
                tempTo.add(transition[1])
            
            else: 
                newTrans.append(transition)

        if len(tempFrom):
            newTrans.append([state, '(' + '+'.join(tempFrom) + ')', i])
        if len(tempTo):
            newTrans.append([i, '(' + '+'.join(tempTo) + ')', state])

    newTrans = []

    for transition in transition_matrix:
        if (transition[0] == state) and (transition[2] == state) and (transition[1] not in selfList):
            selfList.append(transition[1])

        elif (transition[0] == state) and (transition not in fromList):
            fromList.append(transition)

        elif (transition[2] == state) and (transition not in toList):
            toList.append(transition)
        
        else:
            newTrans.append(transition)
    
    selfString = ""
    if len(selfList) and not (len(selfList) == 1 and selfList[0]=="$"):
        selfString = '(' + '+'.join(selfList) + ')' + '*'
    
    for i in toList:
        for j in fromList:

            transString = "("
            if i[1] != "$":
                transString += i[1]
            transString += selfString
            if j[1] != "$":
                transString += j[1]
            if transString == "(":
                transString += "$"
            transString += ")"

            newTrans.append([i[0], transString, j[2]])

    return newTrans


def generateRegex(DFA):
    start_states = DFA["start_states"]
    final_states = DFA["final_states"]
    states = DFA["states"]
    transition_matrix = DFA["transition_function"]

    for i in start_states:
        transition_matrix.append([["Start"], "$", i])
    for i in final_states:
        transition_matrix.append([i, "$", ["Final"]])

    for i in states:
        transition_matrix = removeState(i, transition_matrix, states)

    regexString = ""
    for i in transition_matrix:
        regexString += i[1] + "+"
    regexString = regexString[:-1]

    redRegex =  []
    for i in range(len(regexString)):
        if regexString[i] == "(" and regexString[min(i+2, len(regexString)-1)] == ")":
            continue
        elif regexString[i] == ")" and regexString[max(i-2, 0)] == "(":
            continue
        else:
            redRegex.append(regexString[i])
    
    return "".join(redRegex)


if __name__ == "__main__":
    inFile = sys.argv[1]
    outFile = sys.argv[2]

    with open(inFile, 'r') as readFile:
        DFA = json.load(readFile)

    regex ={
        "regex": generateRegex(DFA)
    } 

    with open(outFile, "w") as writeFile:
        json.dump(regex, writeFile)