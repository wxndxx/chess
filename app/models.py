from dataclasses import dataclass
from enum import StrEnum
from typing import NewType


REVERSE_NOTATION = {0: 'a', 1: 'b', 2: 'c', 3: 'd', 4: 'e', 5: 'f', 6: 'g', 7: 'h'}


Row = NewType("Row", int)
File = NewType("File", int)


class Color(StrEnum):
    WHITE = 'w'
    BLACK = 'b'


class PieceType(StrEnum):
    PAWN = 'p'
    ROOK = 'r'
    KNIGHT = 'n'
    BISHOP = 'b'
    QUEEN = 'q'
    KING = 'k'


SYMBOLS = {
        PieceType.KING: "♚",
        PieceType.QUEEN: "♛",
        PieceType.ROOK: "♜",
        PieceType.BISHOP: "♝",
        PieceType.KNIGHT: "♞",
        PieceType.PAWN: "♟",
    }
RESET = "\033[0m"


@dataclass(frozen=True)
class Square:
    row: Row
    file: File

    def to_notation(self) -> str:
        return REVERSE_NOTATION[self.file] + str(self.row + 1)

    def __repr__(self) -> str:
        return self.to_notation()

    def __post_init__(self):
        if not 0 <= self.row <= 7 or not 0 <= self.file <= 7:
            raise ValueError


@dataclass(frozen=True)
class Move:
    side: Color
    piece: PieceType
    start_square: Square
    end_square: Square
    check: bool = False
    mate: bool = False
    draw: bool = False
    taken_piece: PieceType | None = None
    taken_piece_position: Square | None = None
    promotion: PieceType | None = None

    def to_fen(self) -> str:
        notation = ""
        if self.piece == PieceType.KING:
            if self.end_square.file - self.start_square.file == 2:
                return "O-O"
            if self.start_square.file - self.end_square.file == 2:
                return "O-O-O"
        if self.piece != PieceType.PAWN:
            notation += self.piece.value.upper()
        if self.taken_piece:
            if self.piece == PieceType.PAWN:
                notation += self.start_square.to_notation()[0]
            notation += "x"
        notation += self.end_square.to_notation()
        if self.promotion:
            notation += self.promotion.value.upper()
        if self.check and not self.mate:
            notation += "+"
            return notation
        if self.mate:
            notation += "#"
            return notation
        if self.draw:
            notation += "="
        return notation

    def __repr__(self) -> str:
        return self.to_fen()


class PositionsForCastlingWhite:
    long_rook = Square(row=Row(0), file=File(0))
    short_rook = Square(row=Row(0), file=File(7))
    long_squares = [
        Square(row=Row(0), file=File(1)),
        Square(row=Row(0), file=File(2)),
        Square(row=Row(0), file=File(3))
    ]
    short_squares = [
        Square(row=Row(0), file=File(5)),
        Square(row=Row(0), file=File(6)),
    ]


class PositionsForCastlingBlack:
    long_rook = Square(row=Row(7), file=File(0))
    short_rook = Square(row=Row(7), file=File(7))
    long_squares = [
        Square(row=Row(7), file=File(1)),
        Square(row=Row(7), file=File(2)),
        Square(row=Row(7), file=File(3))
    ]
    short_squares = [
        Square(row=Row(7), file=File(5)),
        Square(row=Row(7), file=File(6)),
    ]
