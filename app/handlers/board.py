from app.handlers.pieces import Piece
from app.models import Color, Square, PieceType


class Board:
    def __init__(self) -> None:
        self.board = [[None] * 8 for _ in range(8)]  # row[file]
        self.white_pieces: set[Piece] = set()
        self.black_pieces: set[Piece] = set()

    def __repr__(self) -> str:
        return self.to_fen()

    def get_piece_in_square(self, square: Square) -> Piece | None:
        return self.board[square.row][square.file]

    def get_king(self, color: Color) -> Piece:
        for row in range(7, -1, -1):
            for piece_in_square in self.board[row]:
                if piece_in_square and piece_in_square.name == PieceType.KING and piece_in_square.color == color:
                    return piece_in_square

    def _get_square_for_display(self, row: int, file: int) -> str:
        square = self.board[row][file]
        return str(square) if isinstance(square, Piece) else "-"

    def display(self) -> None:
        for row in range(7, -1, -1):
            squares = " ".join(
                self._get_square_for_display(row, file)
                for file in range(8)
            )
            print(f"{row + 1} | {squares}")
        print("____________________")
        print("  | a b c d e f g h")

    def add(self, piece: Piece, square: Square) -> None:
        self.board[square.row][square.file] = piece

    def remove(self, square: Square) -> None:
        self.board[square.row][square.file] = None

    def to_fen(self) -> str:
        fen_rows: list[str] = []
        for row in range(7, -1, -1):
            fen_row = []
            empty = 0
            for square in self.board[row]:
                if not square:
                    empty += 1
                else:
                    if empty:
                        fen_row.append(str(empty))
                        empty = 0
                    fen_row.append(repr(square))
            if empty:
                fen_row.append(str(empty))
            fen_rows.append("".join(fen_row))
        return "/".join(fen_rows)

    def get_pieces(self, color: Color) -> list[Piece]:
        pieces = self.white_pieces if color == Color.WHITE else self.black_pieces
        if not pieces:
            for row in range(7, -1, -1):
                for square in self.board[row]:
                    if square and square.color == color:
                        pieces.add(square)
            if color == Color.WHITE:
                self.white_pieces = pieces
            else:
                self.black_pieces = pieces
        return pieces
