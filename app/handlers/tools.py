from app.handlers.pieces import Piece
from app.models import Square, Row, File


def create_and_validate_square(piece: Piece, row_delta: int, file_delta: int) -> Square | None:
    new_row, new_file = (
        piece.position.row + row_delta,
        piece.position.file + file_delta,
    )
    try:
        return Square(row=Row(new_row), file=File(new_file))
    except ValueError:
        return
