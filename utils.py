import chess
import numpy as np
import random

piece_values = {
    "p": 1,
    "n": 2.99,
    "b": 3,
    "r": 5,
    "q": 9.5,
    "k": 50
}

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

def decide_move():

    # Define the environment
    n_states = 1924 # Number of positions (? according to https://ai.stackexchange.com/questions/6923/how-should-i-model-all-available-actions-of-a-chess-game-in-deep-q-learning)
    n_actions = 4 # This would be len(board.legal_moves)
    goal_state = 500  # Current reward count

    # Initialize Q-table with zeros
    Q_table = np.zeros((n_states, n_actions))

    # Define parameters
    learning_rate = 0.8
    discount_factor = 0.95
    exploration_prob = 0.2
    epochs = 1000

    # Q-learning algorithm
    for epoch in range(epochs):
        current_state = random.randint(0, n_states)  # Start from a random state

        while current_state != goal_state:
            # Choose action with epsilon-greedy strategy
            if random.rand() < exploration_prob:
                action = random.randint(0, n_actions)  # Explore
            else:
                action = np.argmax(Q_table[current_state])  # Exploit

            # Simulate the environment (move to the next state)
            # For simplicity, move to the next state
            next_state = (current_state + 1) % n_states

            # Define a simple reward function (1 if the goal state is reached, 0 otherwise)
            reward = 1 if next_state == goal_state else 0

            # Update Q-value using the Q-learning update rule
            Q_table[current_state, action] += learning_rate * \
                (reward + discount_factor *
                np.max(Q_table[next_state]) - Q_table[current_state, action])

            current_state = next_state  # Move to the next state

    # After training, the Q-table represents the learned Q-values
    print("Learned Q-table.")
    #print(Q_table)

