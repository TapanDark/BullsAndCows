import logging
import random
import itertools

class BullsAndCowsPlayer(object):
    def __init__(self):
        self.digitList = ['1','2','3','4','5','6','7','8','9','0']
        self.newGame()

    def newGame(self):
        self.digitIterator = iter(self.digitList)
        self.guessSkeleton = 'XXXX'
        self.lastGuess = '1234'
        self.previousGuesses = {}
        self.uniqueDigits = 0
        self.repeatedDigits=False
        self.triedAllDigits=False
        self.foundAllDigits=False
        self.calculatedPossibles ={}
        self.presentDigitsSet = set()
        self.presentDigitsGroups = []
        self.guessedRepeatList=[]
        self.repeatCount =0

    def guess(self):
        guess = self.guessSkeleton
        if not self.foundAllDigits:
            if self.repeatedDigits:
                logging.debug("Repeated Digits! Repeat count atleast %s Trying digits from %s"%(self.repeatCount, self.presentDigitsSet))
                # TODO: Need logic that will reduce presentDigitsSet
                presentDigitsIterator = iter(self.presentDigitsSet)
                repeatsGuessed=0
                while True:
                    if self.repeatCount >3:
                        import pdb
                        pdb.set_trace()
                        raise Exception("CRITITCAL ERROR!")
                    try:
                        while True:
                            repeatDigit = next(presentDigitsIterator)
                            if repeatDigit not in self.guessedRepeatList and repeatDigit in guess:
                                break
                        guess = guess.replace('X',repeatDigit,self.repeatCount)
                        logging.debug("REPEAT REPLACING %s"% repeatDigit)
                        self.guessedRepeatList.append(repeatDigit)
                        break
                    except StopIteration as e:
                        self.repeatCount +=1
                        logging.debug("Repeat Count increasd to %s"%self.repeatCount)
                        self.guessedRepeatList = []
                        presentDigitsIterator = iter(self.presentDigitsSet)

                presentDigitsIterator = iter(self.presentDigitsSet)
                while 'X' in guess:
                    digit = next(presentDigitsIterator)
                    if digit in list(guess):
                        digit = next(presentDigitsIterator)
                    else:
                        logging.debug("%s not in %s"%(digit,guess))
                        guess = guess.replace('X',digit,1)  
                        logging.debug("NON REPEAT REPLACING %s"% digit)  
            else:
                logging.debug("Still trying new digits!")
                try:
                    while 'X' in guess:
                        guess=guess.replace('X',self.digitIterator.next(),1)
                except StopIteration as e:
                    logging.debug("Out of unguessed digits!")
                    self.triedAllDigits=True
                    cycler = itertools.cycle('90')
                    while 'X' in guess:
                        guess = guess.replace('X',next(cycler), 1)
        else:
            logging.debug("Detected all digits!")
            logging.debug("Number of unique digits: %s"%self.uniqueDigits)
            _ , self.guessSkeleton = max((len(self.calculatedPossibles[key]),key) for key in self.calculatedPossibles)  #  TODO: UPDATE THIS, PICK FROM LIST WHERE KEY HAS MAX BULLS
            guess = self.calculatedPossibles[self.guessSkeleton][0]
            self.guessSkeleton = guess # HACK
        self.lastGuess = guess
        print("Guess: %s"%self.lastGuess)
        if 'X' in guess:   #GIANT HACK
            import pdb
            pdb.set_trace()
        return self.lastGuess

    def processResult(self, result, guess=None):
        if not guess:
            guess = self.lastGuess
        if type(result)!= tuple or len(result)!=2:
            logging.error("Result must be a tuple of lenght 2!")
        if result[0]+result[1] > 0:
            self.presentDigitsGroups.append((result[0]+result[1],set(list(self.lastGuess))))
        self.previousGuesses[guess]=result
        newPossibles = self._getPossibles(result,guess)
        if not self.foundAllDigits:
            self.calculatedPossibles = self._mergeMaskDicts(newPossibles,result)
            if not self.repeatedDigits:
                self.uniqueDigits+=result[0]+result[1]
            if self.uniqueDigits==4:
                self.foundAllDigits = True
            elif self.triedAllDigits:
                if not self.repeatedDigits:  # hack
                    self.repeatCount = 4-sum([item[0] for item in self.presentDigitsGroups])
                self.repeatedDigits=True
                for key in self.calculatedPossibles:  # experimental
                    if self.calculatedPossibles[key][0]:
                        self.guessSkeleton = self.calculatedPossibles[key][0]
                        break
                logging.debug("Repeated Digits Detected!")
        else:
            self.calculatedPossibles = self._filterMaskDict(newPossibles,result)
        for key in self.calculatedPossibles:
            for number in self.calculatedPossibles[key]:
                tempset = set(list(number))
                try:
                    tempset.remove('X')
                except KeyError:
                    pass
                if len(tempset)>4-self.repeatCount:
                    self.calculatedPossibles[key].remove(number)

        self.presentDigitsSet=set()
        # TODO: try to remove ugly, inefficient, nested loop
        for key in self.calculatedPossibles:
            for number in self.calculatedPossibles[key]:
                self.presentDigitsSet.update([digit for digit in number if digit.isdigit()])

        logging.info("Previous possibles %s"%self.calculatedPossibles)
        logging.info("New possibles this round: %s"%newPossibles)
        logging.info("Updated possibles %s"%self.calculatedPossibles)
        logging.info("Possible present digits set %s"%self.presentDigitsSet)
        logging.info("Current guess skeleton %s"%self.guessSkeleton)


    def _getPossibles(self, result,guess):
        def getBullLocations(remainderPositions):
            result = guess
            for position in remainderPositions:
                result = result[:position] + 'X' + result[position+1:]
            return result

        def bullMaskGenerator(bulls, guess):
            for combinationList in itertools.combinations('1234',4-bulls):
                combination = ''.join(combinationList)
                logging.debug("Combination: %s"%combination)
                result = guess
                remainderPositions = []
                for index in combination:
                    remainderPositions.append(int(index)-1)
                    result = result[:int(index)-1] + 'X' + result[int(index):]
                yield result,remainderPositions

        def cowMaskGenerator(cows,guess,bullMaskedString,remainderPositions):
            remainderDigits=[]
            for position in remainderPositions:
                remainderDigits.append(guess[position])
            logging.debug("Remainder Digits: %s"%remainderDigits)
            for combination in itertools.combinations(remainderPositions,cows):
                logging.debug("combination of positions %s"%list(combination))
                for permutation in itertools.permutations(remainderDigits,cows):
                    result = bullMaskedString
                    permutationIterator=iter(permutation)
                    notCool = False
                    for position in combination:
                        digit=next(permutationIterator)
                        if guess[position]==digit:
                            notCool=True
                            break
                        result = result[:position] + digit + result[position+1:]
                    if not notCool:
                        yield result
                    else:
                        continue

        maskedPossibles={}
        for maskedString,remainderPositions in bullMaskGenerator(result[0], guess):
            logging.debug("bullmasked string %s,remainder %s"%(maskedString,remainderPositions))
            maskedPossibles[getBullLocations(remainderPositions)]=[]
            # TODO: remove nasty method of eliminating duplicates
            maskedPossibles[getBullLocations(remainderPositions)].extend(list(set(cowMaskGenerator(result[1],guess,maskedString,remainderPositions))))
            logging.info('New possible this round %s'%maskedPossibles)
        return maskedPossibles

    # TODO: IMPLEMENT THIS
    def _filterMaskDict(self, newPossibles, result):
        keysToRemove = []
        logging.debug("Guess skeleton bulls: %s"%sum(c.isdigit() for c in self.guessSkeleton))
        logging.debug("result bulls %s"%result[0])
        if sum(c.isdigit() for c in self.guessSkeleton) > result[0]:
            logging.debug("deleting key %s"%self.guessSkeleton)
            try:
                del self.calculatedPossibles[self.guessSkeleton]
            except KeyError:
                logging.error("Cant delete key %s"%self.guessSkeleton)
        # elif sum(c.isdigit() for c in self.guessSkeleton) <= result[0]:    #  TODO: NEED TO VERIFY THIS LOGIC!
        #     logging.debug("Found more bulls than are in skeleton! Must update all keys!")
        #     tempDict={}
        #     tempDict[self.guessSkeleton] = self.calculatedPossibles.pop(self.guessSkeleton,None)
        #     self.calculatedPossibles = tempDict

        self.calculatedPossibles = self._mergeMaskDicts(newPossibles, result, combine=False)
        return self.calculatedPossibles

    def _mergeMaskDicts(self, newMaskedDict, result, combine=True):
        def getRelevantSubDict(word, maskedDict):
            returnDict = {}
            for key in maskedDict:
                for index,ltr in [(i,ltr) for i, ltr in enumerate(word) if ltr.isdigit()]:
                    if key[index]!=ltr and key[index]!='X':
                        break
                else:
                    returnDict[key]=maskedDict[key]
            return returnDict

        def combineLists(sourceList, compareList):
            resultList = []
            logging.debug("Combining Lists %s and %s"%(sourceList,compareList))
            for pair in itertools.product(sourceList, compareList):
                temp=""
                for i in range(0,4):   # Block can be improved
                    if pair[0][i]!='X' and pair[1][i]!='X':
                        if pair[0][i]!=pair[1][i]:
                            break
                        else:
                            temp=temp+pair[0][i]
                    elif pair[0][i]=='X' and pair[1][i]=='X':
                        temp = temp+'X'
                    elif pair[0][i]=='X':
                        temp = temp + pair[1][i]
                    else:
                        temp= temp + pair[0][i]
                else:
                    temple = list(temp)
                    temple= set(temple)
                    if 'X' in temple:
                        temple.remove('X')
                    logging.debug("temple is %s"%temple)
                    logging.debug("lenght is %s, repeat count %s"%(len(temple),self.repeatCount))
                    if len(temple)<=4-self.repeatCount:
                        resultList.append(temp)
            logging.debug("combined list is %s"%resultList)
            return resultList

        def filterLists(sourceList, compareList):
            resultList = []
            logging.debug("Filtering List %s with %s"%(sourceList,compareList))
            for number in sourceList:
                for qualifier in compareList:
                    for i in range(0,4):
                        if number[i]!=qualifier[i]:
                            if qualifier[i]!='X':
                                break
                    else:
                        resultList.append(number)
                        break
            logging.debug("Filtered List: %s"%resultList)
            return resultList


        resultMaskedDict={}
        for key in self.calculatedPossibles:
            relevantSubDict = getRelevantSubDict(key, newMaskedDict)
            logging.debug("relavant subdict for key %s is %s"%(key,relevantSubDict))
            for relevantKey in relevantSubDict:
                newkey = key
                if combine:
                    for index,ltr in [(i,ltr) for i, ltr in enumerate(relevantKey) if ltr.isdigit()]:
                        newkey = newkey[:index] + ltr + newkey[index+1:]
                    tempList = combineLists(self.calculatedPossibles[key], relevantSubDict[relevantKey])
                else:
                    tempList = filterLists(self.calculatedPossibles[key], relevantSubDict[relevantKey])
                self._removeImpossibles(tempList, result)

                if tempList:
                    if not newkey in resultMaskedDict:
                        resultMaskedDict[newkey] = []
                    logging.debug("Combination key for %s and %s is %s"%(key, relevantKey, newkey))
                    resultMaskedDict[newkey].extend(tempList)
                    # resultMaskedDict[newkey] = list(set(resultMaskedDict[newkey]))  # TODO : remove crappy way to remove duplicates

        if not self.calculatedPossibles:
            return newMaskedDict
        else:
            return resultMaskedDict

    def _removeImpossibles(self,tempList, result):
        maxCommons = result[0] + result[1]
        cowList=[]
        remainList=[]
        removeList= []
        for number in tempList:
            guessList = list(number)
            commons=0
            for value in list(self.lastGuess):
                if value in guessList:
                    if value!='X':
                        commons+=1
                        guessList.remove(value)
            if commons>maxCommons:
                removeList.append(number)
        for number in removeList:
            while(True):
                try:
                    logging.debug("Removing %s from %s"%(number,tempList))
                    tempList.remove(number)
                except ValueError as e:
                    logging.debug("Last guess %s not in list %s"%(number,tempList))
                    break

if __name__ == '__main__':
    logging.basicConfig(level=0)
    print("Initilizing player")
    player = BullsAndCowsPlayer()
    import pdb
    pdb.set_trace()
    print("Done")
