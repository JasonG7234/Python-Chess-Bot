from utils import *
import random

MAX_DEPTH = 1
def score_moves_recurse(board, count, is_white):
    
    if count >= MAX_DEPTH:
        return None, score_position(board, is_white, to_log=True)
        
    # Turn legal moves into dictionary with scoring
    move_dict = {key: 0 for key in list(board.legal_moves)}
    side = "White" if is_white else "Black"

    count+=1
    for move in list(board.legal_moves):
        # Recurse into moves
        temp_board = board.copy()
        #print(f"Testing move for {side} at depth {count}: {str(move)}")
        temp_board.push(move)
        move_dict[move] = score_moves_recurse(temp_board, count, not is_white)[1]
        
    stack = []
    for _ in range(0, count):
        stack.append(board.peek())
    print(f"Move dict for {side}'s move stack {stack}:")


    # minmax ... if this is the last run, we want the BEST of the LOWEST scores...
    # AKA - We want to choose the move that has the BEST worst-case scenario
    print(move_dict)
    worst_moves = [k for k, v in move_dict.items() if v == min(move_dict.values())]
    #print_moves(board, worst_moves, "    Worst move: ")
    best_moves = [k for k, v in move_dict.items() if v == max(move_dict.values())]
    #print_moves(board, best_moves, "    Best move: ")
    if len(best_moves) == 0:
        return None, 100000 if is_white else -100000
    
    if not is_white:
        print("Choosing best move")
        move = best_moves[random.randint(0, len(best_moves)-1)]
    else:
        print("Choosing worst move")
        move = worst_moves[random.randint(0, len(worst_moves)-1)]
    return move, move_dict[move]

class ChessBot1:
    
    def __init__(self, board, legal_moves):
        self.board = board
        self.legal_moves = legal_moves
        
    def make_move(self):
        moves =  self.__score_moves()
        # Return best move
        print(moves)
        best_moves = [k for k, v in moves.items() if v == max(moves.values())]

        return best_moves[random.randint(0, len(best_moves)-1)]
    
    def __score_moves(self):
        # Turn legal moves into dictionary with scoring
        move_dict = {key: 0 for key in list(self.legal_moves)}
        # Best practices:
        for move in self.legal_moves:
            move_dict[move] = score_move(self.board, move)
        score_position(self.board, False)
        return move_dict

class ChessBot2:
    
    def __init__(self, board, legal_moves):
        self.board = board
        self.legal_moves = legal_moves
        
    def make_move(self):
        move, eval = score_moves_recurse(self.board, 0, False)
        print(move, eval)
        return move

