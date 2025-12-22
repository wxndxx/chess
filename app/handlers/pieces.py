from abc import ABC, abstractmethod

from app.handlers.fen import FEN
from app.models import Square, Color, PieceType, Row, File


class Piece(ABC):
    def __init__(self, color: Color, name: PieceType, position: Square):
        self.color: Color = color
        self.name: PieceType = name
        self.has_moved: bool = False
        self.position: Square = position

    def __repr__(self):
        if self.color == Color.WHITE:
            return self.name.upper()
        return self.name.lower()

    def __str__(self):
        if self.color == Color.WHITE:
            return self.name.upper()
        return self.name.lower()

    @staticmethod
    @abstractmethod
    def get_moves():
        """Get theoretical moves for this piece."""


class SlidingPiece(Piece):
    @staticmethod
    @abstractmethod
    def get_moves() -> tuple[tuple[tuple[int, int]]]: ...


class Pawn(Piece):
    def __init__(self, color: Color, position: Square):
        super().__init__(color=color, name=PieceType.PAWN, position=position)
        self.start_row: int = 1 if self.color == Color.WHITE else 6
        self.direction: int = 1 if self.color == Color.WHITE else -1

    def get_moves(self) -> tuple[tuple[tuple[int, int]]]:
        """Excluding captures"""
        moves = [(self.direction, 0)]
        if self.position.row == self.start_row:
            moves.append((2 * self.direction, 0))
        return (tuple(moves),)


class Rook(SlidingPiece):
    def __init__(self, color: Color, position: Square):
        super().__init__(color=color, name=PieceType.ROOK, position=position)

    @staticmethod
    def get_moves() -> tuple[tuple[tuple[int, int]]]:
        return (
            tuple((i, 0) for i in range(1, 8)),
            tuple((-i, 0) for i in range(1, 8)),
            tuple((0, i) for i in range(1, 8)),
            tuple((0, -i) for i in range(1, 8)),
        )


class Knight(Piece):
    def __init__(self, color: Color, position: Square):
        super().__init__(color=color, name=PieceType.KNIGHT, position=position)

    @staticmethod
    def get_moves() -> tuple[tuple[int, int]]:
        return ((2, 1), (2, -1), (-2, 1), (-2, -1),
                (1, 2), (1, -2), (-1, 2), (-1, -2))


class Bishop(SlidingPiece):
    def __init__(self, color: Color, position: Square):
        super().__init__(color=color, name=PieceType.BISHOP, position=position)

    @staticmethod
    def get_moves() -> tuple[tuple[tuple[int, int]]]:
        return (
            tuple((i, i) for i in range(1, 8)),
            tuple((i, -i) for i in range(1, 8)),
            tuple((-i, i) for i in range(1, 8)),
            tuple((-i, -i) for i in range(1, 8)),
        )


class Queen(SlidingPiece):
    def __init__(self, color: Color, position: Square):
        super().__init__(color=color, name=PieceType.QUEEN, position=position)

    @staticmethod
    def get_moves() -> tuple[tuple[tuple[int, int]]]:
        return (
            tuple((i, i) for i in range(1, 8)),
            tuple((i, -i) for i in range(1, 8)),
            tuple((-i, i) for i in range(1, 8)),
            tuple((-i, -i) for i in range(1, 8)),
            tuple((i, 0) for i in range(1, 8)),
            tuple((-i, 0) for i in range(1, 8)),
            tuple((0, i) for i in range(1, 8)),
            tuple((0, -i) for i in range(1, 8)),
        )


class King(Piece):
    def __init__(self, color: Color, position: Square):
        super().__init__(color=color, name=PieceType.KING, position=position)

    @staticmethod
    def get_moves() -> tuple[tuple[int, int]]:
        return ((1, 0), (-1, 0), (0, 1), (0, -1),
                (1, 1), (1, -1), (-1, 1), (-1, -1))


class PieceFactory:
    @staticmethod
    def get_piece(symbol: str, position: Square) -> Piece:
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


class PieceHandler:
    @classmethod
    def create_pieces(cls, fen: FEN) -> list[Piece]:
        pieces = []
        row_index = 7
        for row in fen.position.split("/"):
            file_index = 0
            for x in row:
                if x.isdigit():
                    file_index = file_index + int(x)
                else:
                    position = Square(row=Row(row_index), file=File(file_index))
                    pieces.append(PieceFactory.get_piece(symbol=x, position=position))
                    file_index += 1
            row_index -= 1
        return pieces
