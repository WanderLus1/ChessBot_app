from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    session,
)

import chess
import chess.engine
import torch
import atexit
import secrets

from src.model import create_model
from src.play import predict_moves


# -------------------------------------------------------
# Flask
# -------------------------------------------------------

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

#stockfish
# -------------------------------------------------------
# Load model once
# -------------------------------------------------------

model = create_model()

model.load_state_dict(
    torch.load(
        "models/bot_v1_1.pth",
        map_location=torch.device("cpu")
    )
)

model.eval()


# -------------------------------------------------------
# Load Stockfish once
# -------------------------------------------------------

engine = chess.engine.SimpleEngine.popen_uci(
    "stockfish/stockfish"
)


# -------------------------------------------------------
# Helper functions
# -------------------------------------------------------

def get_board():

    if "fen" not in session:
        session["fen"] = chess.Board().fen()

    return chess.Board(session["fen"])


def save_board(board):

    session["fen"] = board.fen()


def get_history():

    if "history" not in session:
        session["history"] = []

    return session["history"]


def save_history(history):

    session["history"] = history

def get_uci_history():

    if "uci_history" not in session:
        session["uci_history"] = []

    return session["uci_history"]


def save_uci_history(history):

    session["uci_history"] = history

def get_sources():

    if "sources" not in session:
        session["sources"] = []

    return session["sources"]


def save_sources(sources):

    session["sources"] = sources


def get_ai_color():

    if "ai_color" not in session:
        session["ai_color"] = "black"

    return session["ai_color"]


def save_ai_color(color):

    session["ai_color"] = color


# -------------------------------------------------------
# Home page
# -------------------------------------------------------

@app.route("/")
def index():

    return render_template("index.html")

@app.get("/about")
def about():
    return render_template("about.html")
# -------------------------------------------------------
# Start new game
# -------------------------------------------------------

@app.post("/new_game")
def new_game():

    board = chess.Board()

    history = []

    uci_history = []

    sources = []

    data = request.get_json(silent=True) or {}

    color = data.get("color", "black").lower()

    save_ai_color(color)

    ai_move = None

    if color == "white":

        move, source = predict_moves(
            board=board,
            color=int(board.turn),
            model=model,
            engine=engine,
            k=10
        )

        san = board.san(move)

        board.push(move)

        history.append(san)

        uci_history.append(move.uci())

        sources.append(source)

        ai_move = move.uci()

    save_board(board)
    save_history(history)
    save_uci_history(uci_history)
    save_sources(sources)

    return jsonify({

        "success": True,

        "fen": board.fen(),

        "history": history,

        "moves": uci_history,

        "sources": sources,

        "ai_move": ai_move

    })
# -------------------------------------------------------
# User makes a move
# -------------------------------------------------------

@app.post("/move")
def move():

    board = get_board()

    history = get_history()

    uci_history = get_uci_history()

    sources = get_sources()

    data = request.get_json()

    user_move = data.get("move")

    # ---------------------------------------------
    # User move
    # ---------------------------------------------

    try:

        move = chess.Move.from_uci(user_move)

        if move not in board.legal_moves:

            return jsonify({
                "success": False,
                "message": "Illegal move"
            })

        san = board.san(move)

        board.push(move)

        history.append(san)

        uci_history.append(user_move)

    except Exception:

        return jsonify({
            "success": False,
            "message": "Illegal move"
        })

    # ---------------------------------------------
    # Game over after user's move
    # ---------------------------------------------

    if board.is_game_over(claim_draw=True):

        save_board(board)
        save_history(history)
        save_sources(sources)

        return jsonify({

    "success": True,

    "fen": board.fen(),

    "history": history,

    "moves": uci_history,

    "sources": sources,

    "game_over": True,

    "result": board.result(),

    "termination":
        board.outcome(claim_draw=True).termination.name

})

    # ---------------------------------------------
    # AI move
    # ---------------------------------------------

    ai_move, source = predict_moves(

        board=board,

        color=int(board.turn),

        model=model,

        engine=engine,

        k=10

    )

    san = board.san(ai_move)

    board.push(ai_move)

    history.append(san)

    uci_history.append(ai_move.uci())

    sources.append(source)

    # ---------------------------------------------
    # Save session
    # ---------------------------------------------

    save_board(board)

    save_history(history)

    save_uci_history(uci_history)

    save_sources(sources)

    # ---------------------------------------------
    # Return response
    # ---------------------------------------------

    return jsonify({

        "success": True,

        "fen": board.fen(),

        "history": history,

        "sources": sources,

        "moves": uci_history,

        "ai_move": ai_move.uci(),

        "source": source,

        "game_over": board.is_game_over(claim_draw=True),

        "result": board.result(claim_draw=True) if board.is_game_over(claim_draw=True) else None

    })


# -------------------------------------------------------
# Engine cleanup
# -------------------------------------------------------

@atexit.register
def close_engine():

    try:
        engine.quit()
    except:
        pass


# -------------------------------------------------------
# Run Flask
# -------------------------------------------------------

if __name__ == "__main__":

    app.run(
        debug=True
    )