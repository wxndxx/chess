from app.handlers.fen import FEN
from app.handlers.pieces import Piece, PieceFactory
from app.models import Color, Square, PieceType, Row, File


class Board:
    def __init__(self, fen: FEN, pieces: list[Piece] | None = None) -> None:
        self.board = [[None] * 8 for _ in range(8)]  # row[file]
        self.fen = fen
        self._white_pieces: list[Piece] = list()
        self._black_pieces: list[Piece] = list()
        self._pieces: list[Piece] = pieces if pieces else list()
        self.arrange()

    def __repr__(self) -> str:
        return self.to_fen()

    def get_piece_in_square(self, square: Square) -> Piece | None:
        return self.board[square.row][square.file]

    def _get_square_for_display(self, row: int, file: int) -> str:
        square = self.board[row][file]
        return str(square) if isinstance(square, Piece) else "-"

    def arrange(self) -> None:
        """Arrange pieces on the board"""
        row_index = 7
        for row in self.fen.position.split("/"):
            file_index = 0
            for x in row:
                if x.isdigit():
                    file_index = file_index + int(x)
                else:
                    piece = None
                    position = Square(row=Row(row_index), file=File(file_index))
                    if self._pieces:
                        for piece in self._pieces:
                            if piece.position == position:
                                break
                    else:
                        piece = PieceFactory.get_piece(symbol=x, position=position)
                    self.add(piece, position)
                    file_index += 1
            row_index -= 1

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
        if piece.color == Color.BLACK:
            self._black_pieces.append(piece)
        else:
            self._white_pieces.append(piece)

    def remove(self, square: Square) -> None:
        piece_in_square = self.get_piece_in_square(square)
        if piece_in_square:
            self.get_all_pieces()
            self._pieces.remove(piece_in_square)
            if piece_in_square.color == Color.BLACK:
                self._black_pieces.remove(piece_in_square)
            else:
                self._white_pieces.remove(piece_in_square)
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
        pieces = self._white_pieces if color == Color.WHITE else self._black_pieces
        if not pieces:
            for row in range(7, -1, -1):
                for square in self.board[row]:
                    if square and square.color == color:
                        pieces.append(square)
            if color == Color.WHITE:
                self._white_pieces = pieces
            else:
                self._black_pieces = pieces
        return pieces

    def get_all_pieces(self) -> list[Piece]:
        if not self._pieces:
            for row in range(7, -1, -1):
                for square in self.board[row]:
                    if square:
                        self._pieces.append(square)
        return self._pieces

    def get_king(self, color: Color) -> Piece:
        pieces = self.get_pieces(color)
        for piece in pieces:
            if piece.name == PieceType.KING:
                return piece
