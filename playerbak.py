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
        self.maskedPossibles ={}

    def guess(self):
        guess = self.guessSkeleton
        if not self.foundAllDigits:
            logging.debug("Still trying new digits!")
            try:
                while 'X' in guess:
                    guess=guess.replace('X',self.digitIterator.next(),1)
            except StopIteration as e:
                logging.debug("Out of unguessed digits!")
                self.triedAllDigits=True
                guess = guess.replace('X','9',4)
        else:
            logging.debug("Detected all digits!")
            logging.debug("Number of unique digits: %s"%self.uniqueDigits)
            guess ='1234'
        self.lastGuess = guess
        return self.lastGuess

    def processResult(self, result, guess=None):
        if not guess:
            guess = self.lastGuess
        if type(result)!= tuple or len(result)!=2:
            logging.error("Result must be a tuple of lenght 2!")
        self.previousGuesses[guess]=result
        if not self.foundAllDigits:
            self.uniqueDigits+=result[0]+result[1]
            if self.triedAllDigits:
                self.repeatedDigits=True
                self.foundAllDigits=True
                logging.debug("Repeated Digits Detected!")
        else:
            pass
        self._updatePossibles(result,guess)
        # need to remove duplicates
        logging.info("Final possibles %s"%self.maskedPossibles)

    def _updatePossibles(self,result,guess):
        def getBullLocations(remainderPositions):
            result = 'BBBB'
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

        for maskedString,remainderPositions in bullMaskGenerator(result[0], guess):
            logging.debug("bullmasked string %s,remainder %s"%(maskedString,remainderPositions))
            self.maskedPossibles[getBullLocations(remainderPositions)]=[]
            # TODO: remove nasty method of eliminating duplicates
            self.maskedPossibles[getBullLocations(remainderPositions)].extend(list(set(cowMaskGenerator(result[1],guess,maskedString,remainderPositions))))
            logging.info('Masked Possibles %s'%self.maskedPossibles)

    def _mergeMaskDicts(self, oldMaskedDict, newMaskedDict):
        resultMaskedDict={}
        for key in oldMaskedDict:
            #relevantSubDict = 
            pass

if __name__ == '__main__':
    logging.basicConfig(level=0)
    print("Initilizing player")
    player = BullsAndCowsPlayer()
    import pdb
    pdb.set_trace()
    print("Done")
