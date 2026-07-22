import chess

def position_encoder(board,color):
    position = []
    i = 0
    while(i<64):
        piece = board.piece_at(square=i)
        if(piece == None):
            piece = 0
            position.append(piece)
            i = i + 1
            continue
        if(piece.color):
            position.append(piece.piece_type)
        else:
            position.append((piece.piece_type)*(-1))
        i = i + 1
    move_no = board.fullmove_number
    position.append(move_no)
    position.append(board.has_queenside_castling_rights(True))
    position.append(board.has_kingside_castling_rights(True))
    position.append(board.has_queenside_castling_rights(False))
    position.append(board.has_kingside_castling_rights(False))
    if(board.ep_square == None):
        position.append(0)
    else : position.append(1)
    position.append(color)
    #v1.1 extending the feature vector
    position.append(len(board.pieces(chess.PAWN,chess.WHITE)))
    position.append(len(board.pieces(chess.KNIGHT,chess.WHITE)))
    position.append(len(board.pieces(chess.BISHOP,chess.WHITE)))
    position.append(len(board.pieces(chess.ROOK,chess.WHITE)))
    position.append(len(board.pieces(chess.QUEEN,chess.WHITE)))
    position.append(len(board.pieces(chess.PAWN,chess.BLACK)))
    position.append(len(board.pieces(chess.KNIGHT,chess.BLACK)))
    position.append(len(board.pieces(chess.BISHOP,chess.BLACK)))
    position.append(len(board.pieces(chess.ROOK,chess.BLACK)))
    position.append(len(board.pieces(chess.QUEEN,chess.BLACK)))
    position.append(len(list(board.legal_moves)))
    position.append(board.is_check())
    for square in range(64):
        white_attacks = len(board.attackers(chess.WHITE,square))
        black_attacks = len(board.attackers(chess.BLACK,square))
        if white_attacks == 0 and black_attacks == 0 :
            position.append(10)
            continue
        position.append(white_attacks - black_attacks)
    return position

def move_encoder(move):
    r = move.from_square
    c = move.to_square
    move_id = r * 64 + c
    return move_id

def decode_move(move_id, board):
    from_square = move_id // 64
    to_square = move_id % 64

    piece = board.piece_at(from_square)

    if piece and piece.piece_type == chess.PAWN:
        rank = chess.square_rank(to_square)

        # White pawn reaches 8th rank
        if piece.color == chess.WHITE and rank == 7:
            return chess.Move(from_square, to_square, promotion=chess.QUEEN)

        # Black pawn reaches 1st rank
        if piece.color == chess.BLACK and rank == 0:
            return chess.Move(from_square, to_square, promotion=chess.QUEEN)

    return chess.Move(from_square, to_square)