# Pytanic
Pytanic is a classic 2D programming game. The goal of the game is to pilot a ship around icebergs, islands and sharks. You program the ship's course with simple move and turn commands, then hit start and watch it follow the path you programmed and see if you estimations and logic will take the ship safely to its destination. Hit an iceberg, island or shark and its game over!

## Prerequisites
* Python 3  
`sudo apt install python3`
* Pygame  
`python3 -m pip install -U pygame --user`

## How to use
1. Start `Pytanic.py` from explorer or command line
1. After loading, the command window will display "Captain:". Type your name.
1. Now the command window will display "Ship:". Enter one of the following commands:
   * **move xx** moves the ship in the direction it is pointing (where xx is a numerical distance according to the scale in the bottom right corner)
   * **turn xx** rotates the ship clockwise (where xx is the number of degrees to turn)
1. If the command was entered correctly, a confirmation message will be dislayed in green.
1. If the command was entered wrong, the command window will display a red error message.
1. When all the move/turn commands have been entered, type start to begin.

![Main game screen](screenshots/game_running.png)
