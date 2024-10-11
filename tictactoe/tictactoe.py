"""
Tic Tac Toe Player
"""
import copy
import math

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    counter = 0
    for lines in board:
        for item in lines:
            if item is not EMPTY:
                counter += 1

    if counter % 2 == 0:
        return "X"
    return "O"


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    possible_actions = set()
    for i in range(len(board)):
        for j in range(len(board[i])):
            if board[i][j] is EMPTY:
                possible_actions.add((i, j))

    return possible_actions


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    if action not in actions(board):
        raise Exception()
    else:
        modified_board = copy.deepcopy(board)
        val = player(board)
        modified_board[action[0]][action[1]] = val
        return modified_board


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """

    # check diagonally
    if ((board[0][0] == board[1][1] == board[2][2]) or (board[2][0] == board[1][1] == board[0][2])) \
            and (board[1][1] is not EMPTY):
        return board[1][1]

    # check horizontally
    for i in range(3):
        if (board[i][0] == board[i][1] == board[i][2]) and (board[i][0] is not EMPTY):
            return board[i][0]

    # check vertically
    for i in range(3):
        if (board[0][i] == board[1][i] == board[2][i]) and (board[0][i] is not EMPTY):
            return board[0][i]

    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board) is not None:
        return True

    is_filled = True
    for i in range(3):
        for j in range(3):
            if board[i][j] is EMPTY:
                is_filled = False
                break

    if is_filled:
        return True

    return False


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    terminal_result = winner(board)
    if terminal_result == "X":
        return 1

    if terminal_result == "O":
        return -1

    if terminal_result is None:
        return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if terminal(board):
        return None

    current_player = player(board)

    if current_player == "X":
        return max_value(board)[1]
    else:
        return min_value(board)[1]


def max_value(board):
    if terminal(board):
        return utility(board), None

    best_action = None
    max_val = -math.inf
    for action in actions(board):
        val = min_value(result(board, action))[0]
        if val > max_val:
            max_val = val
            best_action = action

    return max_val, best_action


def min_value(board):
    if terminal(board):
        return utility(board), None

    min_val = math.inf
    best_action = None

    for action in actions(board):
        val = max_value(result(board, action))[0]
        if val < min_val:
            min_val = val
            best_action = action

    return min_val, best_action
