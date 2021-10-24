import sys
import json

states = []
counter = 0
interTransitions = []
transitions = [] 
letters = []


def concat(regex):

    processed = list(regex)
    
    i = 0
    while i < len(processed)-1:
        if (processed[i] == ")" or processed[i] == "*" or processed[i].isalpha() or processed[i].isdigit()) and (processed[i+1].isalpha() or processed[i+1].isdigit()):
            processed.insert(i+1, ".")
            i+=2
            continue
        i += 1
    
    processed = ''.join(processed)
    return str(processed)


def getLetters(string):
    temp = []
    for i in string:
        if (i.isalpha() or i.isdigit()):
            temp.append(i)
    
    return temp



def preprocess(regex):
    global letters
    processed = concat(regex)
    newString = ""

    for i in range (len(processed)):
        if processed[i] == "(":
            newString += "["
        elif processed[i] == ")":
            newString += "],"
        else:
            newString += "'" + processed[i] + "',"
    
    newString = "[" + newString + "]"
    letters = getLetters(newString)
    letters = set(letters)
    letters = list(letters)
    finalList = eval(newString)
    return finalList

def reduceBrackets(regexList):

    if isinstance(regexList, list) == False:
        return regexList

    elif len(regexList) == 1:
        return reduceBrackets(regexList[0])
    
    newList = []

    for i in regexList:
        temp = reduceBrackets(i)
        newList.append(temp)
    
    return newList


def handleKleene(regexList):

    if isinstance(regexList, list) == False:
        return regexList

    newList = []
    for i in regexList:
        if i == "*":
            temp = [newList.pop(), i]
        else:    
            temp = handleKleene(i)      
        newList.append(temp)
    
    return newList


def handleConcat(regexList):
    if isinstance(regexList, list) == False:
        return regexList

    newList = []

    i = 0
    while i < len(regexList):
        temp = handleConcat(regexList[i])
        
        if regexList[max(i-1, 0)] == ".":
            prev = newList.pop()
            prev = newList.pop()
            temp = [prev, regexList[i-1], temp]
        
        newList.append(temp)
        i += 1

    return newList


def handleUnion(regexList):
    if isinstance(regexList, list) == False:
        return regexList

    newList = []

    i = 0
    while i < len(regexList):
        temp = handleUnion(regexList[i])
        
        if regexList[max(i-1, 0)] == "+":
            prev = newList.pop()
            prev = newList.pop()
            temp = [prev, regexList[i-1], temp]
        
        newList.append(temp)
        i += 1

    return newList


def regexParse(regex):
    proRegex = preprocess(regex)
    proRegex = reduceBrackets(proRegex)
    
    proRegex = handleKleene(proRegex)
    proRegex = reduceBrackets(proRegex)

    proRegex = handleConcat(proRegex)
    proRegex = reduceBrackets(proRegex)

    proRegex = handleUnion(proRegex)
    proRegex = reduceBrackets(proRegex)

    return proRegex


def newState():
    global counter
    new = "Q" + str(counter)
    states.append(new)
    counter += 1

    return new


def makeTransition(start, transition, end):
    if isinstance(transition, list):
        interTransitions.append([start, transition, end])
    else:
        transitions.append([start, transition, end])
    

def operateKleene(intTrans):
    start = intTrans[0]
    end = intTrans[2]
    regexTemp = intTrans[1]

    new = newState()

    makeTransition(start, regexTemp[0], new)
    makeTransition(new, "$", end)
    makeTransition(new, regexTemp[0], new)


def operateConcat(intTrans):
    start = intTrans[0]
    end = intTrans[2]
    regexTemp = intTrans[1]

    new = newState()

    makeTransition(start, regexTemp[0], new)
    makeTransition(new, regexTemp[2], end)


def operateUnion(intTrans):
    start = intTrans[0]
    end = intTrans[2]
    regexTemp = intTrans[1]

    makeTransition(start, regexTemp[0], end)
    makeTransition(start, regexTemp[2], end)


def makeNFA(intTrans):
    if intTrans[1][1] == "*":
        operateKleene(intTrans)

    elif intTrans[1][1] == ".":
        operateConcat(intTrans)

    elif intTrans[1][1] == "+":
        operateUnion(intTrans)
            

def generateNFA(parsedNFA):
    start = newState()
    end = newState()
    
    makeTransition(start, parsedNFA, end)

    while len(interTransitions):
        temp = interTransitions.pop()
        makeNFA(temp)

    genNFA = {
        "states": states,
        "letters": letters,
        "transition_matrix": transitions,
        "start_states": [start],
        "final_states": [end]
    }

    return genNFA


if __name__ == "__main__":
    inFile = sys.argv[1]
    outFile = sys.argv[2]

    with open(inFile, 'r') as readFile:
        data = json.load(readFile)

    parsedRegex = regexParse(data["regex"])

    finalNFA = generateNFA(parsedRegex)

    with open(outFile, "w") as writeFile:
        json.dump(finalNFA, writeFile)