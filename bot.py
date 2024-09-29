from utils import *
import random

class ChessBot:
    
    def __init__(self, board, legal_moves):
        self.board = board
        self.legal_moves = legal_moves
        
    def make_move(self):
        moves =  self.__score_moves()
        # Return best move
        best_moves = [k for k, v in moves.items() if v == max(moves.values())]

        return best_moves[random.randint(0, len(best_moves)-1)]
    
    def __score_moves(self):
        # Turn legal moves into dictionary with scoring
        move_dict = {key: 0 for key in list(self.legal_moves)}
        # Best practices:
        for move in self.legal_moves:
            # 1 - Recapture taken pieces
            last_move, last_board = get_last_move_and_board_state(self.board)
            if (last_board.is_capture(last_move) and
                move.to_square == last_move.to_square):
                # Capture back
                move_dict[move] += (get_piece_value(self.board.piece_at(move.to_square)) - get_piece_value(self.board.piece_at(last_move.to_square)))
            
            # 2 - Capture pieces
            if (self.board.is_capture(move)):
                print("CAPTURE")
                if (square_is_safe(self.board, move.to_square)):
                    move_dict[move] += get_piece_value(self.board.piece_at(move.to_square))
                else:
                    move_dict[move] += (get_piece_value(self.board.piece_at(move.to_square)) - get_piece_value(self.board.piece_at(move.from_square)))

            
            # 3 - Castle
            if (self.board.has_castling_rights(self.board.turn)
            and piece_making_move(self.board, move) == "k"):
                print("kING AND CAN CASTLE")
                if move.to_square - move.from_square > 1: # Castling
                    move_dict[move] += 0.5
                else:
                    move_dict[move] -= 0.5

            # Move to safe squares
            if (square_is_safe(self.board, move.to_square)):
                if (square_is_safe(self.board, move.from_square)):
                # If the piece is already safe, then it's not a big deal to move to a safe square
                    move_dict[move] += 0.9
                else:
                    move_dict[move] += get_piece_value(self.board.piece_at(move.from_square))
                
            # Activate minor pieces
            if (self.board.fullmove_number < 10 and 
                (piece_making_move(self.board, move) == "b" and str(move.from_square) in ["c8", "f8"]) or
                (piece_making_move(self.board, move) == "n" and str(move.from_square) in ["b8", "g8"])):
                move_dict[move] += 0.75
            
            # 5 - Promote pawns
            if (piece_making_move(self.board, move) == "p"
            and move.to_square > 60):
                print("CAN PROMOTE")
                if (square_is_safe(self.board, move.to_square)):
                    move_dict[move] += 8.6 # Queen is 9.5, minus 0.9 for the safe square check already done
                else:
                    move_dict[move] += 0.9 # idk
            
            # 6 - Try not to move backwards
            if (chess.square_rank(move.to_square) > chess.square_rank(move.from_square)):
                move_dict[move] -= (chess.square_rank(move.to_square) - chess.square_rank(move.from_square))/8
            
            # 7 - Check number of squares we can attack with a move
            move_dict[move] += 0.1*new_squares_attacked(self.board, move)
            
            # Get rooks to open ranks and then 7th rank
            # Look for knight forks
        
        return move_dict
        
#class LearnerBot:

class ChessEnvironment:
    def __init__(self, board, color):
        self.board = board
        self.color = color
        #self.game_over = False
        
    def step(self, move):
        '''
        Step should represent each move, I imagine
        '''
        
        # Make the move
        self.board.push(move)
        
        # Check if the game is over
        if self.board.outcome():
            self.board.reset()
            return self.board.fen(), 500 if self.board.outcome().winner == self.color else -500, True
        
        # Calculate scoring otherwise
        # Check point value of positions
        # Moving pawn forward should be number of points at rank
        # Moving to a protected square should be loss of points
        return self.board.fen(), 0, False


env = ChessEnvironment()
state = env.reset()
done = False
while not done:
    move = decide_move()
    state, reward, done = env.step(move)
    print(f"State: {state}, Reward: {reward}")