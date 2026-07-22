import torch
from src.encoder import position_encoder,decode_move
from src.model import create_model
import chess
import chess.engine
#stockfish
def predict_moves(board, color, model, engine, k=10):
    model.eval()

    # ----------------------------
    # Pure Stockfish in endgames
    # ----------------------------
    if len(board.piece_map()) <= 8:
        result = engine.play(
            board,
            chess.engine.Limit(depth=14)
        )
        print(f"[ENDGAME] Stockfish plays: {result.move}")
        return result.move ,"ENDGAME"

    # ----------------------------
    # Neural network predictions
    # ----------------------------
    x = position_encoder(board, color)
    x = torch.tensor(x, dtype=torch.float32).unsqueeze(0)

    with torch.no_grad():
        logits = model(x)

    scores, indices = torch.topk(logits, k=100)

    candidate_moves = []
    candidate_probs = []

    for score, move_id in zip(scores[0], indices[0]):
        move = decode_move(move_id.item(), board)

        if move in board.legal_moves:
            candidate_moves.append(move)
            candidate_probs.append(score.item())

        if len(candidate_moves) == k:
            break

    # ----------------------------
    # Stockfish best move + score
    # ----------------------------
    info = engine.analyse(
        board,
        chess.engine.Limit(depth=14)
    )

    best_score = info["score"].relative.score(mate_score=100000)

    score = info["score"].relative

    # Forced mate
    if score.is_mate():
        result = engine.play(
           board,
           chess.engine.Limit(depth=14)
        )

        print("[MATE] Stockfish plays:", result.move)
        return result.move, "OVERRIDE"

    # Huge evaluation
    if abs(best_score) >= 800:
        result = engine.play(
            board,
            chess.engine.Limit(depth=14)
        )

        print("[WINNING] Stockfish plays:", result.move)
        return result.move, "OVERRIDE"

    THRESHOLD = 90  # centipawns

    # ----------------------------
    # Filter bad candidate moves
    # ----------------------------
    for move, prob in zip(candidate_moves, candidate_probs):

        board.push(move)

        info = engine.analyse(
            board,
            chess.engine.Limit(depth=14)
        )

        move_score = info["score"].relative.score(mate_score=100000)

        board.pop()

        # Convert score back to current side's perspective
        move_score = -move_score

        loss = best_score - move_score

        if loss <= THRESHOLD:
            print(f"[MODEL] {move} accepted ({loss:.0f} cp worse than Stockfish)")
            return move ,"MODEL"

    # ----------------------------
    # Everything was bad -> Stockfish
    # ----------------------------
    result = engine.play(
        board,
        chess.engine.Limit(depth=14)
    )

    print(f"[OVERRIDE] Stockfish plays {result.move} (all model moves > {THRESHOLD} cp worse)")
    return result.move ,"OVERRIDE"



def play(model, user_color=chess.WHITE):
    board = chess.Board()
    engine = chess.engine.SimpleEngine.popen_uci("stockfish/stockfish")
    print("User color:", user_color)
    print("Board turn:", board.turn)
    while not board.is_game_over():

        print(board)
        print()

        if board.turn == user_color:

            while True:
                user_move = input("Your move: ")

                try:
                    board.push_uci(user_move)
                    break
                except:
                    print("Illegal move. Try again.")

        else:

            move = predict_moves(
                board,
                color=int(board.turn),
                model=model,
                engine=engine,
                k=10
            )

            print("Model plays:", move)
            board.push(move)

    engine.quit()

    print(board)
    print("\nGame Over:", board.result())