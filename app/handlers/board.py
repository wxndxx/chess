from app.handlers.pieces import Piece, PieceFactory
from app.models import (
    Color,
    Square,
    PieceType,
    Move,
    PositionsForCastlingBlack,
    PositionsForCastlingWhite,
)
from app.tools import is_short_castling, is_long_castling, create_and_validate_square


class Board:
    def __init__(self, pieces: list[Piece]) -> None:
        self.board = [[None] * 8 for _ in range(8)]  # row[file]
        self.arrange(pieces)

    def __repr__(self) -> str:
        return self.to_fen()

    def get_piece_in_square(self, square: Square) -> Piece | None:
        return self.board[square.row][square.file]

    def _get_square_for_display(self, row: int, file: int) -> str:
        square = self.board[row][file]
        return str(square) if isinstance(square, Piece) else "-"

    def arrange(self, pieces: list[Piece]) -> None:
        """Arrange pieces on the board"""
        for piece in pieces:
            self.add(piece, piece.position)

    def make_move(self, move: Move) -> Piece | None:
        taken_piece = None
        moved_piece = self.get_piece_in_square(move.start_square)
        if move.taken_piece:
            taken_piece = self.get_piece_in_square(move.taken_piece_position)
            self.remove(move.taken_piece_position)
        self.remove(square=move.start_square)
        if move.promotion:
            symbol = (
                move.promotion.lower()
                if move.side == Color.BLACK
                else move.promotion.upper()
            )
            promoted_piece = PieceFactory.get_piece(symbol, move.end_square)
            self.add(piece=promoted_piece, square=move.end_square)
        else:
            moved_piece.position = move.end_square
            self.add(piece=moved_piece, square=move.end_square)
        if is_short_castling(move):
            short_rook = self._get_short_rook(move.side)
            self.remove(short_rook.position)
            short_rook.position = create_and_validate_square(
                short_rook, row_delta=0, file_delta=-2
            )
            self.add(piece=short_rook, square=short_rook.position)
        if is_long_castling(move):
            long_rook = self._get_long_rook(move.side)
            self.remove(long_rook.position)
            long_rook.position = create_and_validate_square(
                long_rook, row_delta=0, file_delta=+3
            )
            self.add(piece=long_rook, square=long_rook.position)
        return taken_piece

    def undo_move(self, move: Move, taken_piece: Piece | None = None) -> None:
        moved_piece = self.get_piece_in_square(move.end_square)
        moved_piece.position = move.start_square
        if taken_piece:
            self.add(piece=taken_piece, square=move.end_square)
        else:
            self.remove(square=move.end_square)
        if move.promotion:
            symbol = (
                move.promotion.lower()
                if move.side == Color.BLACK
                else move.promotion.upper()
            )
            moved_piece = PieceFactory.get_piece(symbol, move.start_square)
        self.add(piece=moved_piece, square=move.start_square)
        if is_short_castling(move):
            rook_square = create_and_validate_square(
                moved_piece, row_delta=0, file_delta=1
            )
            short_rook = self.get_piece_in_square(rook_square)
            self.remove(rook_square)
            short_rook.position = (
                PositionsForCastlingBlack.short_rook
                if move.side == Color.BLACK
                else PositionsForCastlingWhite.short_rook
            )
            self.add(piece=short_rook, square=short_rook.position)
        if is_long_castling(move):
            rook_square = create_and_validate_square(
                moved_piece, row_delta=0, file_delta=-1
            )
            long_rook = self.get_piece_in_square(rook_square)
            self.remove(rook_square)
            long_rook.position = (
                PositionsForCastlingBlack.long_rook
                if move.side == Color.BLACK
                else PositionsForCastlingWhite.long_rook
            )
            self.add(piece=long_rook, square=long_rook.position)

    def display(self) -> None:
        for row in range(7, -1, -1):
            squares = " ".join(
                self._get_square_for_display(row, file) for file in range(8)
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
        pieces = []
        if not pieces:
            for row in range(7, -1, -1):
                for square in self.board[row]:
                    if square and square.color == color:
                        pieces.append(square)
        return pieces

    def get_all_pieces(self) -> list[Piece]:
        pieces = []
        for row in range(7, -1, -1):
            for square in self.board[row]:
                if square:
                    pieces.append(square)
        return pieces

    def get_king(self, color: Color) -> Piece:
        pieces = self.get_pieces(color)
        for piece in pieces:
            if piece.name == PieceType.KING:
                return piece

    def _get_short_rook(self, color: Color) -> Piece:
        if color == Color.BLACK:
            return self.get_piece_in_square(PositionsForCastlingBlack.short_rook)
        return self.get_piece_in_square(PositionsForCastlingWhite.short_rook)

    def _get_long_rook(self, color: Color) -> Piece:
        if color == Color.BLACK:
            return self.get_piece_in_square(PositionsForCastlingBlack.long_rook)
        return self.get_piece_in_square(PositionsForCastlingWhite.long_rook)
