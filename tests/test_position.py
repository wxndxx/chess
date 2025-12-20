import pytest

from app.handlers.board import Board
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
            16,
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
    ],
)
def test_possible_moves(fen_string, must_have, must_not_have, expected_len):
    fen = FEN(fen_string)
    board = Board(fen=fen)
    position_handler = PositionHandler(fen=fen, board=board)
    moves = position_handler.get_possible_moves()
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
    board = Board(fen=fen)
    position_handler = PositionHandler(fen=fen, board=board)
    moves = position_handler.get_possible_moves()
    str_moves = [move.to_fen() for move in moves]
    for move in must_have:
        assert move in str_moves

    for move in must_not_have:
        assert move not in str_moves
