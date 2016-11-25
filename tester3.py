from game import BullsAndCowsGame
from player4 import BullsAndCowsPlayer
#import logging

if __name__=='__main__':
    # logging.basicConfig(level=0)
    game = BullsAndCowsGame()
    player = BullsAndCowsPlayer()
    for i in range(0000,10000):
        if len(set(list('%04d'%i))) != 4:
            continue
        else:
            result = (0,0)
            game.newGame(secret='%04d'%i)
            player.newGame()
            while result[0]!=4:
                result=game.evaluate(player.guess())
                player.processResult(result)
            if game.attempts>9:
                print("FAILING NUMBER %s"%i)
                break

# Bad numbers: 9481-9487

# BAD NUMBERS : 6819, 7369, 8042, 9183, 9743 
