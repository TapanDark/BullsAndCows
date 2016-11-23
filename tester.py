from game import BullsAndCowsGame
from player3 import BullsAndCowsPlayer
import logging

if __name__=='__main__':
    # logging.basicConfig(level=0)
    game = BullsAndCowsGame()
    game.newGame(secret='9485')
    player = BullsAndCowsPlayer()
    result = (0,0)
    while result[0]!=4:
        result=game.evaluate(player.guess())
        player.processResult(result)


# Bad numbers: 9481-9487
