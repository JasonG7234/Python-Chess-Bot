import chess
import chess.svg
import time

from chessboard import display

from bot import ChessBot1, ChessBot2

if __name__ == "__main__":
    board = chess.Board()
    
    game_board = display.start()

    while not board.is_checkmate():
        if board.turn == chess.WHITE:
            move = input("What is your move? ")
            if (move == "fen"):
                print(board.fen())
            try:
                board.push_san(move)
            except Exception as e:
                print("That is an invalid move. Try again.")
        else:
            move = ChessBot2(board, board.legal_moves).make_move()
            print("The bot plays " + str(move))
            board.push(move)
        
        display.update(board.fen(), game_board)
        #time.sleep(2)
    
    print("Game over!")
    display.terminate()

#make_move()

    #check if in check
    # check if endgame table / mate in X
    # score moves
    
#visualize moves