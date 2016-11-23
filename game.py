import random

class BullsAndCowsGame(object):

    def __init__(self):
        self.newGame()

    def newGame(self, secret=None, maxAttempts=10):
        if not secret:
            self.secret = str(random.randint(1000,9999))
        else:
            self.secret = secret
        self.secretList = list(self.secret)
        self.attempts=1
        self.maxAttemptsAllowed=maxAttempts

    def evaluate(self, guess):
        guessList = list(guess)
        guessList = [s for s in guessList if s.isdigit()]
        bulls=0
        cows=0
        cowList=[]
        remainList=[]
        if len(guessList)!=4:
            print("Guess must contain exactly 4 numbers!")
            return None
        if self.attempts<self.maxAttemptsAllowed:
            for index,value in enumerate(self.secretList):
                if guessList[index]==value:
                    bulls+=1
                else:
                    cowList.append(value)
                    remainList.append(guessList[index])
            if cowList:
                for number in cowList:
                    if number in remainList:
                        cows+=1
                        remainList.remove(number)
            if bulls == 4:
                print("You win! Answer is %s. Attempts %s"%(self.secret,self.attempts))
                return (bulls,cows)
            else:
                print("Bulls %s, Cows %s"%(bulls,cows))
            self.attempts +=1
            return (bulls,cows)
        else:
            print("You are out of attempts! Game Over!")
            print("The secret number was %s"%self.secret)
            return None

if __name__=="__main__":
    logging.info("Starting Game")
    game = BullsAndCowsGame()
    import pdb
    pdb.set_trace()
    logging.info("Done!")
