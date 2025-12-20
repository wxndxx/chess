import pytest

from app.handlers.position import Position
from app.handlers.fen import FEN


@pytest.mark.parametrize(
    "fen_string, must_have, must_not_have, expected_len",
    [
        (
            "4k3/8/8/8/8/8/8/N3K3 w - - 0 1",
            {"Nc2"},
            {"Nc3"},
            7,
        ),
        (
            "4k3/8/8/8/8/8/8/B6K w - - 0 1",
            {"Bh8"},
            {"Bb3"},
            10,
        ),
        (
            "4k3/8/8/8/8/8/8/R3K3 w - - 0 1",
            {"Rb1", "Ra7"},
            {"Rg8"},
            16,
        ),
        (
            "4k3/8/8/8/8/8/8/Q3K3 w - - 0 1",
            {"Qb1", "Qa7", "Qg7"},
            {"Qh1"},
            22,
        ),
        (
            "4k3/8/8/8/8/8/7P/4K3 w - - 0 1",
            {"h3", "h4"},
            {"g3"},
            7,
        ),
        (
            "4k3/8/8/7q/8/8/8/R3K3 w - - 0 1",
            {"Kf1"},
            {"Kc1"},
            13,
        ),
    ],
)
def test_possible_moves(fen_string, must_have, must_not_have, expected_len):
    fen = FEN(fen_string)
    position_handler = Position(fen=fen)
    position_handler.arrange(create=True)
    moves = position_handler.get_possible_moves()
    str_moves = [move._to_fen() for move in moves]

    for move in must_have:
        assert move in str_moves

    for move in must_not_have:
        assert move not in str_moves

    assert len(moves) == expected_len


@pytest.mark.parametrize(
    "fen_string, must_have, must_not_have",
    [
        (
            "rnbqkbnr/ppppp1pp/8/4Pp2/8/8/PPPP1PPP/RNBQKBNR w KQkq f6 0 1",
            {"e6", "exf6"},
            {"d6"},
        ),
        (
            "rnbqkbnr/ppppp1pp/8/4Pp2/8/8/PPPP1PPP/RNBQKBNR w KQkq - 0 1",
            {"e6"},
            {"f6", "d6"},
        )
    ]
)
def test_en_passant_moves(fen_string, must_have, must_not_have):
    fen = FEN(fen_string)
    position_handler = Position(fen=fen)
    moves = position_handler.get_possible_moves()
    str_moves = [move._to_fen() for move in moves]
    for move in must_have:
        assert move in str_moves

    for move in must_not_have:
        assert move not in str_moves


# @pytest.mark.parametrize(
#     "fen_string, position, result",
#     [
#         (
#             "rnbqkbnr/pppppppp/6Q1/8/8/8/PP1PPPPP/RNB1K1NR w KQkq - 0 1",
#             (6, 5),
#             "Qxf7+"
#         ),
#         (
#             "rnbqkbnr/ppp1p1pp/3p2P1/7B/8/8/PP1PPPPP/RNB1K1NR w KQkq - 0 1",
#             (6, 7),
#             "gxh7+"
#         ),
#         (
#             "rnb1kbnr/ppppp1pp/6R1/7B/8/8/PPqPPP1P/RNB1K1NR w KQkq - 0 1",
#             (5, 2),
#             "Rc6+"
#         )
#     ],
# )
# def test_check(fen, position, result):
#     engine = Engine(fen)
#     move = engine.make_a_move(piece=engine.white_pieces[0], position=Position(position[0], position[1]))
#     assert result == move
#
#
# @pytest.mark.parametrize(
#     "fen, position, result",
#     [
#         (
#             "rnbqkbnr/ppppp2p/8/8/6B1/8/PP1PPP1P/RNB1K1NR w KQkq - 0 1",
#             (4, 7),
#             "Bh5#"
#         ),
#         (
#             "rnbqkbnr/ppppp2p/6P1/7B/8/8/PP1PPP1P/RNB1K1NR w KQkq - 0 1",
#             (6, 7),
#             "gxh7#"
#         ),
#         (
#             "rnbqkbnr/ppppp2p/5P2/7B/8/8/PP1PPP1P/RNB1K1NR w KQkq - 0 1",
#             (6, 5),
#             "f7#"
#         ),
#         (
#             "rnbqkbnr/ppp1p2p/3p2P1/7B/8/8/PP1PPP1P/RNB1K1NR w KQkq - 0 1",
#             (6, 7),
#             "gxh7+"
#         )
#     ],
# )
# def test_mate(fen, position, result):
#     engine = Engine(fen)
#     move = engine.make_a_move(piece=engine.white_pieces[0], position=Position(position[0], position[1]))
#     assert result == move
#
#
# @pytest.mark.parametrize(
#     "fen, position, result",
#     [
#         (
#             "4k3/4B3/8/4Q3/8/8/8/4K3 w - - 0 1",
#             (5, 4),
#             "Qe6="
#         ),
#         (
#             "4k3/8/3Q4/5Q2/8/8/8/4K3 w - - 0 1",
#             (5, 5),
#             "Qf6="
#         ),
#         (
#             "4k3/4p3/8/Pp2P2p/1PpR1R1P/2Pp4/3P4/4K3 w - - 0 1",
#             (5, 4),
#             "e6="
#         )
#     ],
# )
# def test_draw(fen, position, result):
#     engine = Engine(fen)
#     move = engine.make_a_move(piece=engine.white_pieces[1], position=Position(position[0], position[1]))
#     assert result == move
#
#
# def test_multiple_moves():
#     fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
#     engine = Engine(fen)
#     moves = engine.get_possible_moves()
#     assert len(moves) == 20
#     engine.make_a_move(engine.white_pieces[4], Position(3, 4))
#     moves = engine.get_possible_moves()
#     assert len(moves) == 20
#     engine.make_a_move(engine.black_pieces[12], Position(4, 4))
#     moves = engine.get_possible_moves()
#     assert len(moves) == 29