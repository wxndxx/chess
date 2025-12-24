import pytest

from app.handlers.board import Board
from app.handlers.pieces import PieceHandler
from app.handlers.position import PositionHandler
from app.handlers.fen import FEN


@pytest.mark.parametrize(
    "fen_string, must_have, must_not_have, expected_len",
    [
        pytest.param(
            "4k3/8/8/8/8/8/8/N3K3 w - - 0 1",
            {"Nc2"},
            {"Nc3"},
            7,
            id="Knight moves"
        ),
        pytest.param(
            "4k3/8/8/8/8/8/8/B6K w - - 0 1",
            {"Bh8"},
            {"Bb3"},
            10,
            id="Bishop moves"
        ),
        pytest.param(
            "4k3/8/8/8/8/8/8/R3K3 w - - 0 1",
            {"Rb1", "Ra7"},
            {"Rg8"},
            15,
            id="Rook moves"
        ),
        pytest.param(
            "4k3/8/8/8/8/8/8/Q3K3 w - - 0 1",
            {"Qb1", "Qa7", "Qg7"},
            {"Qh1"},
            22,
            id="Queen moves"
        ),
        pytest.param(
            "4k3/8/8/8/8/8/7P/4K3 w - - 0 1",
            {"h3", "h4"},
            {"g3"},
            7,
            id="Pawn moves"
        ),
        pytest.param(
            "4k3/8/8/7q/8/8/8/R3K3 w - - 0 1",
            {"Kf1", "Kf2", "Kd2"},
            {"Kc1", "Kd1"},
            13,
            id="King moves"
        ),
        pytest.param(
            "rnbqkbnr/pppp1ppp/8/4p3/2P5/8/PP1PPPPP/RNBQKBNR w KQkq e6 0 1",
            {"Nf3"},
            {"Ne2", "Be2", "Bg2", "Qd2", "Rh2", "Ra2", "Nd2", "Bb2", "Bd2"},
            22,
            id="Taking your pieces"
        ),
        pytest.param(
            "k7/6P1/8/8/8/8/8/K7 w - - 0 1",
            {"g8B", "g8Q", "g8R", "g8N"},
            {"g8"},
            7,
            id="Pawn promotion"
        ),
        pytest.param(
            "k4n2/6P1/8/8/8/8/8/K7 w - - 0 1",
            {"gxf8B", "gxf8Q", "gxf8R", "gxf8N"},
            {"g8", "gxf8"},
            11,
            id="Pawn promotion with taking a piece"
        ),
        pytest.param(
            "3rk3/8/8/8/8/8/8/R3K2R w KQ - 0 1",
            {"O-O", "Rd1"},
            {"O-O-O", "Kd1"},
            23,
            id="Castle through check"
        )
    ],
)
def test_possible_moves(fen_string, must_have, must_not_have, expected_len):
    fen = FEN(fen_string)
    pieces = PieceHandler.create_pieces(fen)
    board = Board(pieces)
    position = PositionHandler(board=board, move_order=fen.move_order, en_passant=fen.en_passant, castling=fen.castles)
    moves = position.get_possible_moves()
    str_moves = [move.to_fen() for move in moves]

    for move in must_have:
        assert move in str_moves

    for move in must_not_have:
        assert move not in str_moves

    assert len(moves) == expected_len


@pytest.mark.parametrize(
    "fen_string, must_have, must_not_have",
    [
        pytest.param(
            "rnbqkbnr/ppppp1pp/8/4Pp2/8/8/PPPP1PPP/RNBQKBNR w KQkq f6 0 1",
            {"e6", "exf6"},
            {"d6"},
            id="En passant take"
        ),
        pytest.param(
            "rnbqkbnr/ppppp1pp/8/4Pp2/8/8/PPPP1PPP/RNBQKBNR w KQkq - 0 1",
            {"e6"},
            {"f6", "d6"},
            id="No en passant"
        )
    ]
)
def test_en_passant_moves(fen_string, must_have, must_not_have):
    fen = FEN(fen_string)
    pieces = PieceHandler.create_pieces(fen)
    board = Board(pieces)
    position = PositionHandler(board=board, move_order=fen.move_order, en_passant=fen.en_passant, castling=fen.castles)
    moves = position.get_possible_moves()
    str_moves = [move.to_fen() for move in moves]
    for move in must_have:
        assert move in str_moves

    for move in must_not_have:
        assert move not in str_moves
