from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import StrEnum


@dataclass
class Position:
    row: int
    file: int

    def __post_init__(self):
        if not 0 <= self.row <= 7 or not 0 <= self.file <= 7:
            raise ValueError


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


class Piece(ABC):
    def __init__(self, color: Color, name: PieceType, position: Position):
        self.color: Color = color
        self.name: PieceType = name
        self.has_moved: bool = False
        self.position: Position = position

    def __repr__(self):
        if self.color == Color.WHITE:
            return self.name.upper()
        return self.name.lower()

    @abstractmethod
    def get_moves(self) -> tuple[int, int]:
        """Get possible piece moves"""

    def get_possible_moves(self) -> list[Position]:
        moves = self.get_moves()
        possible_moves = []
        for row_delta, file_delta in moves:
            try:
                new_position = Position(row=self.position.row + row_delta, file=self.position.file + file_delta)
                possible_moves.append(new_position)
            except ValueError:
                pass
        return possible_moves


class Pawn(Piece):
    def __init__(self, color: Color, position: Position):
        super().__init__(color=color, name=PieceType.PAWN, position=position)

    def get_moves(self) -> tuple[tuple[int, int]]:
        ...


class Rook(Piece):
    def __init__(self, color: Color, position: Position):
        super().__init__(color=color, name=PieceType.ROOK, position=position)

    def get_moves(self) -> tuple[tuple[int, int]]:
        ...


class Knight(Piece):
    def __init__(self, color: Color, position: Position):
        super().__init__(color=color, name=PieceType.KNIGHT, position=position)

    def get_moves(self) -> tuple[tuple[int, int]]:
        return ((2, 1), (2, -1), (-2, 1), (-2, -1),
                (1, 2), (1, -2), (-1, 2), (-1, -2))


class Bishop(Piece):
    def __init__(self, color: Color, position: Position):
        super().__init__(color=color, name=PieceType.BISHOP, position=position)

    def get_moves(self) -> tuple[tuple[int, int]]:
        ...


class Queen(Piece):
    def __init__(self, color: Color, position: Position):
        super().__init__(color=color, name=PieceType.QUEEN, position=position)

    def get_moves(self) -> tuple[tuple[int, int]]:
        ...


class King(Piece):
    def __init__(self, color: Color, position: Position):
        super().__init__(color=color, name=PieceType.KING, position=position)

    def get_moves(self) -> tuple[tuple[int, int]]:
        return ((1, 0), (-1, 0), (0, 1), (0, -1),
                (1, 1), (1, -1), (-1, 1), (-1, -1))


class PieceFactory:
    @staticmethod
    def get_piece(symbol: str, position: Position):
        if symbol.isupper():
            color = Color.WHITE
        else:
            color = Color.BLACK
        match symbol.lower():
            case PieceType.PAWN:
                return Pawn(color=color, position=position)
            case PieceType.ROOK:
                return Rook(color=color, position=position)
            case PieceType.KNIGHT:
                return Knight(color=color, position=position)
            case PieceType.BISHOP:
                return Bishop(color=color, position=position)
            case PieceType.QUEEN:
                return Queen(color=color, position=position)
            case PieceType.KING:
                return King(color=color, position=position)
