import chess
import random
import sys
import math

piece_values = {
    "p": 1,
    "n": 3,
    "b": 3.1,
    "r": 5,
    "q": 9.5,
    "k": 50
}

knight_pesto_table = {
    1: -112.5, 2: -63.5, 3: -23.5, 4: -38.5, 5: 15.0, 6: -62.0, 7: -39.0, 8: -103.0, 9: -49.0, 10: -24.5, 11: 23.5, 12: 17.0, 13: 7.0, 14: 18.5, 15: -8.5, 16: -34.5, 17: -35.5, 18: 20.0, 19: 23.5, 20: 37.0, 21: 41.5, 22: 60.0, 23: 27.0, 24: 1.5, 25: -13.0, 26: 10.0, 27: 20.5, 28: 37.5, 29: 29.5, 30: 40.0, 31: 13.0, 32: 2.0, 33: -15.5, 34: -1.0, 35: 16.0, 36: 19.0, 37: 22.0, 38: 18.0, 39: 12.5, 40: -13.0, 41: -23.0, 42: -6.0, 43: 5.5, 44: 12.5, 45: 14.5, 46: 7.0, 47: 2.5, 48: -19.0, 49: -35.5, 50: -36.5, 51: -11.0, 52: -4.0, 53: -1.5, 54: -1.0, 55: -18.5, 56: -31.5, 57: -67.0, 58: -36.0, 59: -40.5, 60: -24.0, 61: -19.5, 62: -23.0, 63: -34.5
}

center_squares = [
    "e4", "e5", "d4", "d5"
]

def num_minor_pieces(board):
    return (
        board.pieces(chess.KNIGHT, chess.WHITE)+board.pieces(chess.KNIGHT, chess.BLACK)+ # Knights
        board.pieces(chess.BISHOP, chess.WHITE)+board.pieces(chess.BISHOP, chess.BLACK)+ # Bishops
        board.pieces(chess.ROOK, chess.WHITE)+board.pieces(chess.ROOK, chess.BLACK) # Rooks
    )
    # Under 7 == end game, under 11 == middle game

def get_last_move_and_board_state(board):
    
    last_board = board.copy()
    last_move = last_board.pop()
    return last_move, last_board

def piece_making_move(board, move):
    '''
    Gets the symbol p, n, b, r, q, k for the black pieces.
    '''
    return board.piece_at(move.from_square)
    
def square_is_safe(board, square):
    return len(board.attackers(chess.WHITE, square)) == 0
    
def get_piece_value(piece):
    return piece_values[piece.symbol().lower()]

def new_squares_attacked(board, move):
    board_copy = board.copy()
    board_copy.push(move)
    t = squares_attacked(board_copy)-squares_attacked(board)
    return t

def squares_attacked(board):
    '''
    Gets the number of squares being attacked with a board state.
    '''
    attackers_count = 0
    for square in chess.SQUARES:
        attackers_count += len(board.attackers(chess.WHITE, square))
    return attackers_count

def is_open_file(board, square):
    file = chess.square_file(square)
    for file_in_front in range(file, 8):
        if board.piece_at(chess.square(file_in_front, chess.square_rank(square)) == "p"):
            return False
    return True

def score_move(board, move):
    '''
    Returns arbitrary score of a move.
    '''
    score = 0
    # 1 - Recapture taken pieces
    last_move, last_board = get_last_move_and_board_state(board)
    if (last_board.is_capture(last_move) and
        move.to_square == last_move.to_square):
        # Capture back
        score += (get_piece_value(board.piece_at(move.to_square)) - get_piece_value(board.piece_at(last_move.to_square)))
    
    # 2 - Capture pieces
    if (board.is_capture(move)):
        print("CAPTURE")
        if (square_is_safe(board, move.to_square)):
            score += get_piece_value(board.piece_at(move.to_square))
        else:
            score += (get_piece_value(board.piece_at(move.to_square)) - get_piece_value(board.piece_at(move.from_square)))

    
    # 3 - Castle
    if (board.has_castling_rights(board.turn)
    and piece_making_move(board, move) == "k"):
        print("kING AND CAN CASTLE")
        if move.to_square - move.from_square > 1: # Castling
            score += 0.5
        else:
            score -= 0.5

    # Move to safe squares
    if (square_is_safe(board, move.to_square)):
        if (square_is_safe(board, move.from_square)):
        # If the piece is already safe, then it's not a big deal to move to a safe square
            score += 0.9
        else:
            score += get_piece_value(board.piece_at(move.from_square))
        
    # Activate minor pieces
    if (board.fullmove_number < 10 and 
        (piece_making_move(board, move) == "b" and str(move.from_square) in ["c8", "f8"]) or
        (piece_making_move(board, move) == "n" and str(move.from_square) in ["b8", "g8"])):
        score += 0.75
    
    # 5 - Promote pawns
    if (piece_making_move(board, move) == "p"
    and move.to_square > 60):
        print("CAN PROMOTE")
        if (square_is_safe(board, move.to_square)):
            score += 8.6 # Queen is 9.5, minus 0.9 for the safe square check already done
        else:
            score += 0.9 # idk
    
    # 6 - Try not to move backwards
    if (chess.square_rank(move.to_square) > chess.square_rank(move.from_square)):
        score -= (chess.square_rank(move.to_square) - chess.square_rank(move.from_square))/8
    
    # 7 - Check number of squares we can attack with a move
    score += 0.1*new_squares_attacked(board, move)
    
    # Get rooks to open ranks and then 7th rank
    if piece_making_move(board, move) == "r":
        score += 0.5 if chess.square_rank(move.to_square) == 7 else 0
        
        if is_open_file(board, move.to_square):
            score += 0.5
    return score

def score_piece_count(board, is_white, to_log=False):
    
    white_pts = (len(board.pieces(chess.PAWN, chess.WHITE))*1
        + len(board.pieces(chess.KNIGHT, chess.WHITE))*3
        + len(board.pieces(chess.BISHOP, chess.WHITE))*3.1
        + len(board.pieces(chess.ROOK, chess.WHITE))*5
        + len(board.pieces(chess.PAWN, chess.WHITE))*9.5
    )
    black_pts = (len(board.pieces(chess.PAWN, chess.BLACK))*1
        + len(board.pieces(chess.KNIGHT, chess.BLACK))*3
        + len(board.pieces(chess.BISHOP, chess.BLACK))*3.1
        + len(board.pieces(chess.ROOK, chess.BLACK))*5
        + len(board.pieces(chess.PAWN, chess.BLACK))*9.5
    )
    if (to_log):
        print(f"Piece eval: {white_pts-black_pts if is_white else black_pts-white_pts}")
    return white_pts-black_pts if is_white else black_pts-white_pts

def score_position(board, is_white, to_log=False):
    if (board.outcome()):
        if (is_white and board.outcome().winner == chess.WHITE or
            not is_white and board.outcome().winner == chess.BLACK):
            return 10000
        else:
            return -10000
    
    score = score_piece_count(board, is_white, to_log)
    score += score_board_state(board, is_white, to_log)
    return score

def __points_score_pieces_hanging(board, is_white, to_log):
    piece_types = [chess.PAWN, chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN]
    side = chess.WHITE if is_white else chess.BLACK
    
    score_hanging_pieces = 0
    for piece in piece_types:
        squares = board.pieces(piece, side)
        for square in squares: 
            val = get_piece_value(board.piece_at(square))
            # Get list of attackers and defenders of each piece
            attacker_squares = board.attackers(chess.WHITE if not is_white else chess.BLACK, square)
            
            defender_squares = board.attackers(chess.WHITE if is_white else chess.BLACK, square)
            
            # If there are multiple attackers and multiple defenders, get the point values 
            attackers = []
            defenders = []
            for sq in attacker_squares:
                if to_log: print(f"Attacker Square @ {chess.square_name(sq)}")
                attackers.append(get_piece_value(board.piece_at(sq)))
            for sq in defender_squares:
                if to_log: print(f"Defender Square @ {chess.square_name(sq)}")
                defenders.append(get_piece_value(board.piece_at(sq)))
            
            attackers = sorted(attackers)
            if to_log: print(f"Attackers @ {chess.square_name(square)}: {attackers}")
            defenders = sorted(defenders)
            if to_log: print(f"Defenders @ {chess.square_name(square)}: {defenders}")

            for i in range(0, len(attackers)):
                attack_value = val - attackers[i]

                # The piece being attacked is more important than the piece attacking, so we will take the exchange
                if (attack_value > 0):
                    if to_log: print(f"[-{attack_value}] Piece @ {chess.square_name(square)} is worth more than attacker @ {list(attacker_squares)[i]}.")
                    score_hanging_pieces -= attack_value
                    break
                    
                # The piece in question is undefended
                elif (len(defenders)-1 < i):
                    if to_log: print(f"[-{val}] No defender for piece @ {chess.square_name(square)} from attacker @ {list(attacker_squares)[i]}.")
                    score_hanging_pieces -= val
                    break

    return score_hanging_pieces

def __points_pawn_score_from_starting_rank(square, is_white, to_log=False):
    '''
    Checks the square a pawn is on and scores 0.1 for each rank it is past it's original.
    Score: 0.1x
    '''
    rank = chess.square_rank(square)
    score = 0.1*(rank-1 if is_white else 6-rank)
    if to_log:
        print(f"Pawn on rank {rank} is worth {score}.")
    return score

def __points_knight_score_on_square(square, is_white, to_log=False):
    '''
    Checks the square a knight is on and scores it according to a PeSTO table
    Score: 0.1x(avg(https://www.chessprogramming.org/PeSTO%27s_Evaluation_Function))
    '''
    score = 0.1*knight_pesto_table[int(square) if is_white else 63-int(square)]
    if to_log:
        print(f"Knight on {chess.square_name(square)} ({square}) is worth {score}.")
    return score

def __points_bishop_score_protecting_center(square, board, to_log=False):
    score = 0
    attacked_squares = board.attacks(square)
    for a_sq in attacked_squares:
        if chess.square_name(a_sq) in center_squares:
            if to_log:
                print(f"[+0.1] Bishop attacks center square {chess.square_name(a_sq)}.")
    return score

def __points_bishop_score_no_mobility(square, board, to_log=False):
    score = 0
    attacked_squares = board.attacks(square)
    for a_sq in attacked_squares:
        if chess.square_name(a_sq) in FORWARD_SQUARES:
            if to_log:
                print(f"[+0.1] Bishop attacks center square {chess.square_name(a_sq)}.")
    return score

def __points_rook_score_on_open_file(square, board, is_white, to_log=False):
    '''
    Checks the square a rook is on and scores 0.5 if it does not have one of its own pawns on it.
    Score: 0.5|0
    '''
    for i in range(1, 8):
        sq = chess.square(chess.square_file(square), i)
        if board.piece_at(sq) and board.piece_at(sq).symbol() == ("P" if is_white else "p"):
            if to_log:
                print(f"[0] Pawn on {chess.square_name(sq)} disrupts rook on file {chess.square_file(square)}.")
            return 0
    if to_log:
        print(f"[+0.5] Rook on file {chess.square_name(square)[0]} has an open file.")
    return 0.5

def __points_rook_score_if_stacked(sq1, sq2, to_log):
    '''
    Checks the square both rooks are on and scores 0.5 if they can see each other.
    Score: 0.5|0
    '''
    # TODO: Ensure the rooks do not have any pieces in between.
    same_rank = chess.square_rank(sq1) == chess.square_rank(sq2)
    same_file = chess.square_file(sq1) == chess.square_file(sq2)
    if same_rank:
        if to_log: print(f"[+0.5] Rooks are on the same rank {chess.square_rank(sq1)}.")
        return 0.5
    elif same_file:
        if to_log: print(f"[+0.5] Rooks are on the same file {chess.square_file(sq1)}.")
    else:
        if to_log: print(f"[0] Rooks are not on the same file or rank.")
        return 0

def __points_rook_score_on_seventh_rank(square, is_white, to_log=False):
    '''
    Checks the square a rook is on and scores 0.5 if it is on the second (or seventh) rank.
    Score: 0.5|0
    '''
    on_second_to_last_rank = chess.square_rank(square)==7 if is_white else chess.square_rank(square)==2
    if on_second_to_last_rank:
        if to_log:
            print(f"[+0.5] Rook on {chess.square_name(square)} is on the second to last rank.")
        return 0.5
    else:
        if to_log:
            print(f"[0] Rook on {chess.square_name(square)} is not on the second to last rank.")
        return 0
    
def score_board_state(board, is_white, to_log=False):
    '''
    Scores a position.
    '''
    score = 0
    side = chess.WHITE if is_white else chess.BLACK
    
    #TODO: is piece hanging? 
    score+= __points_score_pieces_hanging(board, is_white, to_log)
    
    # Evaluate checks
    if board.is_check():
        if to_log: print("[+1] There is a check." if board.turn != side else "[-1] There is a check.")
        score += 1 if board.turn != side else -1
        
    pawns = board.pieces(chess.PAWN, side)
    for pawn in pawns:
        score+= __points_pawn_score_from_starting_rank(pawn, is_white, to_log)
        #TODO: num pawns protect themselves, or pawns that aren't attacked
        
    knights = board.pieces(chess.KNIGHT, side)
    for knight in knights:
        score+= __points_knight_score_on_square(knight, is_white, to_log)
        
    bishops = board.pieces(chess.BISHOP, side)
    # get bishops on good diagonals? protecting the middle?
    for bishop in bishops:
        score+= __points_bishop_score_protecting_center(bishop, board, to_log)
        #score+= __points_bishop_score_no_mobility(bishop, board, to_log)
        
    rooks = board.pieces(chess.ROOK, side)
    list_rooks = list(rooks)
    if len(rooks) > 1: score+= __points_rook_score_if_stacked(list_rooks[0], list_rooks[1], to_log)
    for rook in rooks:
        score+=__points_rook_score_on_seventh_rank(rook, is_white, to_log)
        score+=__points_rook_score_on_open_file(rook, board, is_white, to_log)
        
    # Evaluate king safety
    
    return score
    
    
    
    
    