import chess
import sys
from chessboard import display
from utils import *

board = chess.Board()
board.set_fen(sys.argv[1])
    
game_board = display.start()
print("Our simple evaluation puts this position at eval: " + str(score_position(board, True, to_log=True)) + " for white.")

display.update(board.fen(), game_board)
import time
time.sleep(10000)
