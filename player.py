import logging
import random
import itertools

class BullsAndCowsPlayer(object):
    def __init__(self):
        self.digitList = ['1','2','3','4','5','6','7','8','9','0']
        self.digitIterator = iter(self.digitList)
        self.newGame()

    def newGame(self):
        self.guessSkeleton = 'XXXX'
        self.lastGuess = '1234'
        self.previousGuesses = {}
        self.knownDigits = 0
        self.repeatedDigits=False
        self.triedAllDigits=False
        self.maskedPossibles =[]

    def guess(self):
        guess = self.guessSkeleton
        if self.knownDigits!=4:
            try:
                while 'X' in guess:
                    guess=guess.replace('X',self.digitIterator.next(),1)
            except StopIteration as e:
                logging.debug("Out of unguessed digits!")
                self.triedAllDigits=True
                guess = guess.replace('X','9',4)
        else:
            logging.debug("Detected all digits!")
            guess ='1234'
        self.lastGuess = guess
        return self.lastGuess

    def processResult(self, result, guess=None):
        if not guess:
            guess = self.lastGuess
        if type(result)!= tuple or len(result)!=2:
            logging.error("Result must be a tuple of lenght 2!")
        self.previousGuesses[guess]=result
        if self.knownDigits!=4:
            self.knownDigits+=result[0]+result[1]
            if self.triedAllDigits:
                self.repeatedDigits=True
                self.knownDigits=4
                logging.debug("Repeated Digits Detected!")
        self._updatePossibles(result,guess)
        # need to remove duplicates
        logging.info("Final possibles %s"%self.maskedPossibles)

    def _updatePossibles(self,result,guess):
        for maskedString,remainderPositions in self._bullMaskGenerator(result[0], guess):
            logging.debug("bullmasked string %s,remainder %s"%(maskedString,remainderPositions))
            self.maskedPossibles.extend(self._cowMaskGenerator(result[1],guess,maskedString,remainderPositions))
            logging.info('Masked Possibles %s'%self.maskedPossibles)

    def _bullMaskGenerator(self,bulls, guess):
        for combinationList in itertools.combinations('1234',4-bulls):
            combination = ''.join(combinationList)
            logging.debug("Combination: %s"%combination)
            result = guess
            remainderPositions = []
            for index in combination:
                remainderPositions.append(int(index)-1)
                result = result[:int(index)-1] + 'X' + result[int(index):]
            yield result,remainderPositions

    def _cowMaskGenerator(self,cows,guess,bullMaskedString,remainderPositions):
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

if __name__ == '__main__':
    logging.basicConfig(level=0)
    print("Initilizing player")
    player = BullsAndCowsPlayer()
    import pdb
    pdb.set_trace()
    print("Done")
