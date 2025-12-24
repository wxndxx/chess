import functools
import time

from app.handlers.pieces import Piece
from app.models import Square, Row, File, Color, Move, PieceType


NOTATION = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}


def create_and_validate_square(piece: Piece, row_delta: int, file_delta: int) -> Square | None:
    new_row, new_file = (
        piece.position.row + row_delta,
        piece.position.file + file_delta,
    )
    try:
        return Square(row=Row(new_row), file=File(new_file))
    except ValueError:
        return


def get_next_color(color: Color) -> Color:
    if color == color.WHITE:
        return color.BLACK
    return color.WHITE


def is_short_castling(move: Move) -> bool:
    if move.piece == PieceType.KING:
        if move.start_square.file + 2 == move.end_square.file:
            return True
    return False


def is_long_castling(move: Move) -> bool:
    if move.piece == PieceType.KING:
        if move.start_square.file - 2 == move.end_square.file:
            return True
    return False


def notation_to_square(notation: str) -> Square:
    str_file, str_row = notation
    return Square(row=Row(int(str_row) - 1), file=File(NOTATION[str_file]))


def measure_time(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"{func.__name__} executed in {elapsed:.2f} seconds")
        return result

    return wrapper
