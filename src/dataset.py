import numpy as np
import chess
import chess.pgn
from src.config import accounts
from src.encoder import position_encoder,move_encoder

def build_dataset(files):
    X = []
    y = []

    for file in files:

        pgn = open(file)

        while True:
            game = chess.pgn.read_game(pgn)

            if game is None:
                break

            process_game(game, X, y)

        pgn.close()

    X = np.array(X)
    y = np.array(y)

    return X, y

def get_color(game):
    if(game.headers["White"] in accounts):
        return 1
    else:
        return 0

def process_game(game, X, y):
    color = get_color(game)
    board = game.board()

    for move in game.mainline_moves():

        if(color == board.turn):
            X.append(position_encoder(board, color))
            y.append(move_encoder(move))

        board.push(move)