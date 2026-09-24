import pytest

from app.models import Move, Color, PieceType
from app.tools import notation_to_square


@pytest.mark.parametrize(
    "piece, start_square, end_square, promotion, taken_piece, uci, fen",
    [
        pytest.param(
            "p",
            "e2",
            "e4",
            None,
            None,
            "e2e4",
            "e4",
            id="Pawn push"
        ),
        pytest.param(
            "b",
            "c1",
            "h6",
            None,
            "p",
            "c1h6",
            "Bxh6",
            id="Bishop takes pawn"
        ),
        pytest.param(
            "k",
            "e1",
            "g1",
            None,
            None,
            "e1g1",
            "O-O",
            id="Short castle"
        ),
        pytest.param(
            "k",
            "e1",
            "c1",
            None,
            None,
            "e1c1",
            "O-O-O",
            id="Long castle"
        ),
        pytest.param(
            "p",
            "e7",
            "e8",
            "q",
            None,
            "e7e8q",
            "e8Q",
            id="Pawn promotion"
        ),
        pytest.param(
            "p",
            "d7",
            "e8",
            "q",
            "r",
            "d7e8q",
            "dxe8Q",
            id="Pawn promotion with a capture"
        ),
    ]
)
def test_notation(piece, start_square, end_square, promotion, taken_piece, uci, fen):
    move = Move(
        side=Color.WHITE,
        piece=PieceType(piece),
        start_square=notation_to_square(start_square),
        taken_piece=PieceType(taken_piece) if taken_piece else None,
        end_square=notation_to_square(end_square),
        promotion=PieceType(promotion) if promotion else None,
    )
    assert move.to_uci() == uci
    assert move.to_fen() == fen
