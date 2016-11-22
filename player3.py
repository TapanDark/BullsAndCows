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

    def guess(self):
        guess = self.guessSkeleton
        if not self.foundAllDigits:
            if self.repeatedDigits:
                logging.debug("Repeated Digits! Trying digits from %s"%self.presentDigitsSet)
                while 'X' in guess:
                    guess = guess.replace('X',next(iter(self.presentDigitsSet)),1)
            else:
                logging.debug("Still trying new digits!")
                try:
                    while 'X' in guess:
                        guess=guess.replace('X',self.digitIterator.next(),1)
                except StopIteration as e:
                    logging.debug("Out of unguessed digits!")
                    self.triedAllDigits=True
                    guess = guess.replace('X','9', 4)
        else:
            logging.debug("Detected all digits!")
            logging.debug("Number of unique digits: %s"%self.uniqueDigits)
            for key in self.calculatedPossibles:  #experimental
                if self.calculatedPossibles[key][0]:
                    guess = self.calculatedPossibles[key][0]
                    self.guessSkeleton = key
                    break
        self.lastGuess = guess
        return self.lastGuess

    def processResult(self, result, guess=None):
        if not guess:
            guess = self.lastGuess
        if type(result)!= tuple or len(result)!=2:
            logging.error("Result must be a tuple of lenght 2!")
        self.previousGuesses[guess]=result
        newPossibles = self._updatePossibles(result,guess)
        if not self.foundAllDigits:
            self.calculatedPossibles = self._mergeMaskDicts(newPossibles)
            self.uniqueDigits+=result[0]+result[1]
            if self.uniqueDigits==4:
                self.foundAllDigits = True
            elif self.triedAllDigits:
                self.repeatedDigits=True
                for key in self.calculatedPossibles:  #experimental
                    if self.calculatedPossibles[key][0]:
                        self.guessSkeleton = self.calculatedPossibles[key][0]
                        break
                logging.debug("Repeated Digits Detected!")
        else:
            self.calculatedPossibles = self._filterMaskDict(newPossibles,result)

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


    def _updatePossibles(self,result,guess):
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
        elif sum(c.isdigit() for c in self.guessSkeleton) <= result[0] > 4:    #  TODO: NEED TO VERIFY THIS LOGIC!
            self.calculatedPossibles = self.calculatedPossibles.pop(self.guessSkeleton,None)

        for key in self.calculatedPossibles:
            for number in self.calculatedPossibles[key]:
                pass

        return self.calculatedPossibles

    def _mergeMaskDicts(self, newMaskedDict):
        def getRelevantSubDict(word, maskedDict):
            returnDict = {}
            for key in maskedDict:
                for index in [i for i, ltr in enumerate(word) if ltr.isdigit()]:
                    if key[index]!='X':
                        break
                else:
                    returnDict[key]=maskedDict[key]
            return returnDict

        def combineLists(sourceList, compareList):
            resultList = []
            logging.debug("Combining Lists %s and %s"%(sourceList,compareList))
            for pair in itertools.product(sourceList, compareList):
                temp=""
                for i in range(0,4):
                    if pair[0][i]!='X' and pair[1][i]!='X':
                        break
                    if pair[0][i]=='X' and pair[1][i]=='X':
                        temp = temp+'X'
                    elif pair[0][i]=='X':
                        temp = temp + pair[1][i]
                    else:
                        temp= temp + pair[0][i]
                else:
                    resultList.append(temp)
            logging.debug("combined list is %s"%resultList)
            return resultList

        resultMaskedDict={}
        for key in self.calculatedPossibles:
            relevantSubDict = getRelevantSubDict(key, newMaskedDict)
            logging.debug("relavant subdict for key %s is %s"%(key,relevantSubDict))
            for relevantKey in relevantSubDict:
                newkey = key
                for index,ltr in [(i,ltr) for i, ltr in enumerate(relevantKey) if ltr.isdigit()]:
                    newkey = newkey[:index] + ltr + newkey[index+1:]
                if not newkey in resultMaskedDict:
                    resultMaskedDict[newkey] = []
                logging.debug("Combination key for %s and %s is %s"%(key, relevantKey, newkey))
                resultMaskedDict[newkey].extend(combineLists(self.calculatedPossibles[key], relevantSubDict[relevantKey]))

        if not self.calculatedPossibles:
            return newMaskedDict
        else:
            return resultMaskedDict

if __name__ == '__main__':
    logging.basicConfig(level=0)
    print("Initilizing player")
    player = BullsAndCowsPlayer()
    import pdb
    pdb.set_trace()
    print("Done")
