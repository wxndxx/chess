import pytest

from app.handlers.board import Board
from app.handlers.fen import FEN
from app.handlers.move import MoveHandler
from app.handlers.pieces import PieceHandler
from app.handlers.position import PositionHandler


@pytest.mark.parametrize(
    "fen_string, must_have, must_not_have",
    [
        pytest.param(
            "k7/r7/8/8/8/8/R7/K7 w - - 0 1",
            {"Ra3", "Rxa7+"},
            {"Rb2", "Ra1", "Ra8"},
            id="Pinned rook"
        ),
        pytest.param(
            "k6b/8/8/8/8/8/1P6/K7 w - - 0 1",
            {"Kb1", "Ka2"},
            {"b3", "b4"},
            id="Pinned pawn"
        ),
        pytest.param(
            "k6b/8/8/8/8/2P5/8/K7 w - - 0 1",
            {"Kb1", "Ka2", "Kb2"},
            {"c4"},
            id="Pinned remote pawn"
        ),
        pytest.param(
            "2k5/8/8/8/8/8/4R3/2K5 w - - 0 1",
            {"Rc2+", "Re8+"},
            {"Rb2+"},
            id="Basic rook check"
        ),
        pytest.param(
            "2k5/8/3P4/8/8/8/8/2K5 w - - 0 1",
            {"d7+"},
            {"d8"},
            id="Basic pawn check"
        ),
        pytest.param(
            "2k5/8/8/5N2/8/8/8/2K5 w - - 0 1",
            {"Nd6+", "Ne7+"},
            {"Nd5+", "Nh4+"},
            id="Basic knight check"
        ),
        pytest.param(
            "k7/8/6B1/8/8/8/8/2K5 w - - 0 1",
            {"Be4+"},
            {"Bg2+"},
            id="Basic bishop check"
        ),
        pytest.param(
            "k7/8/8/8/8/8/K7/R7 w - - 0 1",
            {"Kb3+", "Kb2+", "Kb1+"},
            {"Ka3+"},
            id="Discovered check"
        ),
        pytest.param(
            "5KN1/4N2k/4pB1p/4PPpP/6P1/8/8/8 w - g6 0 1",
            {"fxg6#", "hxg6#"},
            {"fxg6+", "hxg6+", "Rh8+", "fxg6=", "hxg6=", "Rh8="},
            id="En passant mate"
        ),
        pytest.param(
            "1k6/8/1K6/8/8/8/7R/8 w - - 0 1",
            {"Rh8#"},
            {"Rh8+"},
            id="Back rank mate"
        ),
        pytest.param(
            "1k4NR/8/1K6/8/8/8/8/8 w - - 0 1",
            {"Nf6#", "Nh6#", "Ne7#"},
            {"Nf6+", "Nh6+"},
            id="Discovered mate"
        ),
        pytest.param(
            "rnbqkbnr/1pppppp1/p6p/7B/2Q1P3/8/PPPP1PPP/RNB1K1NR w KQkq - 0 1",
            {"Qxf7#", "Bxf7#"},
            {"Qxf7+", "Bxf7+"},
            id="Mate with taking a pawn"
        ),
        pytest.param(
            "kr6/pp6/8/1N6/8/8/8/1K6 w - - 0 1",
            {"Nc7#"},
            {"Nxa7#"},
            id="Smothered mate"
        ),
        pytest.param(
            "k7/8/1Q6/7p/8/7P/8/1K6 w - - 0 1",
            {"h4="},
            {"Qb7#"},
            id="Stalemate"
        ),
        pytest.param(
            "1k3n2/6P1/1K6/8/8/8/8/8 w - - 0 1",
            {"gxf8Q#", "gxf8R#"},
            {"gxf8Q+", "gxf8R+", "g8Q+", "gxf8B+"},
            id="Back rank mate with pawn promotion"
        )
    ]
)
def test_move_generation(fen_string, must_have, must_not_have):
    fen = FEN(fen_string)
    pieces = PieceHandler.create_pieces(fen)
    board = Board(pieces)
    position = PositionHandler(board=board, move_order=fen.move_order, en_passant=fen.en_passant)
    move_handler = MoveHandler(board)
    moves = []
    for move in position.get_possible_moves():
        final_move, _ = move_handler.check_move(move)
        if final_move:
            moves.append(final_move.to_fen())

    for move in must_have:
        assert move in moves
    for move in must_not_have:
        assert move not in moves
