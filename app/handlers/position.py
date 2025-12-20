from functools import cache

from app.handlers.fen import FEN
from app.handlers.tools import create_and_validate_square
from app.models import (
    Color,
    Square,
    Move,
    Row,
    File,
    PieceType,
    PositionsForCastlingBlack,
    PositionsForCastlingWhite,
)
from app.handlers.board import Board
from app.handlers.pieces import Piece, SlidingPiece, Pawn, Knight, King, PieceFactory


class Position:
    def __init__(self, fen: FEN, pieces: set[Piece] | None = None):
        self.board: Board = Board()
        self.fen: FEN = fen
        self.pieces = pieces if pieces else set()
        if self.pieces:
            create = False
        else:
            create = True
        self.arrange(create=create)
        opponent_color = self._get_opponent_color()
        self.attack_handler: AttackHandler = AttackHandler(
            board=self.board,
            opponent_color=opponent_color,
            opponent_pieces=self.get_pieces_by_color(opponent_color),
        )

    def is_check(self) -> bool:
        king = self._get_king(self.fen.move_order)
        if king.position in self.attack_handler.get_attacked_squares():
            return True
        return False

    def is_mate(self) -> bool:
        king = self._get_king(self.fen.move_order)
        king_moves = self._get_king_moves(king)
        if king in self.attack_handler.get_attacked_squares() and len(king_moves) == 0:
            return True
        return False

    def is_draw(self) -> bool:
        king = self._get_king(self.fen.move_order)
        possible_moves = self.get_possible_moves()
        if king not in self.attack_handler.get_attacked_squares() and len(possible_moves) == 0:
            return True
        return False

    def arrange(self, create: bool) -> None:
        """Arrange pieces on the board"""
        row_index = 7
        for row in self.fen.position.split("/"):
            file_index = 0
            for x in row:
                if x.isdigit():
                    file_index = file_index + int(x)
                else:
                    position = Square(row=Row(row_index), file=File(file_index))
                    piece = self.get_piece_by_position(position=position, piece_name=x, create=create)
                    if piece:
                        self.pieces.add(piece)
                    self.board.board[row_index][file_index] = piece
                    file_index += 1
            row_index -= 1

    def get_pieces_by_color(self, color: Color) -> set[Piece]:
        pieces = set()
        if len(self.pieces) > 0:
            for piece in self.pieces:
                if piece.color == color:
                    pieces.add(piece)
        return pieces

    def get_piece_by_position(
        self, position: Square, piece_name: PieceType, create: bool = False
    ) -> Piece | None:
        if create:
            return PieceFactory.get_piece(symbol=piece_name, position=position)
        for piece in self.pieces:
            if piece.position == position:
                return piece

    @cache
    def get_possible_moves(self) -> set[Move]:
        """Get all theoretical possible moves"""
        moves = set()
        pieces = self.board.get_pieces(self.fen.move_order)
        for piece in pieces:
            moves.update(self._get_piece_moves(piece))
        return moves

    def _get_piece_moves(self, piece: Piece) -> set[Move]:
        match piece:
            case SlidingPiece():
                return self._get_sliding_piece_moves(piece)
            case Pawn():
                return self._get_pawn_moves(piece)
            case Knight():
                return self._get_knight_moves(piece)
            case King():
                return self._get_king_moves(piece)

    def _get_sliding_piece_moves(self, piece: SlidingPiece | Pawn) -> set[Move]:
        moves = set()
        for ray in piece.get_moves():
            for row_delta, file_delta in ray:
                square = create_and_validate_square(piece, row_delta, file_delta)
                if not square:
                    break
                piece_in_square = self.board.get_piece_in_square(square)
                if piece_in_square:
                    if piece_in_square.color != piece.color:
                        if not isinstance(piece_in_square, Pawn):
                            move = Move(
                                piece=piece,
                                start_square=piece.position,
                                end_square=square,
                                taken_piece=piece_in_square,
                            )
                            moves.add(move)
                    break
                else:
                    move = Move(
                        piece=piece, start_square=piece.position, end_square=square
                    )
                    moves.add(move)
        return moves

    def _get_pawn_moves(self, pawn: Pawn) -> set[Move]:
        moves = self._get_sliding_piece_moves(pawn)
        for side in (-1, 1):
            square = create_and_validate_square(pawn, pawn.direction, side)
            if square:
                piece_in_square = self.board.get_piece_in_square(square)
                if piece_in_square and piece_in_square.color != pawn.color:
                    move = Move(
                        piece=pawn,
                        start_square=pawn.position,
                        end_square=square,
                        taken_piece=piece_in_square,
                    )
                    moves.add(move)
                if square.to_notation() == self.fen.en_passant:
                    move = Move(
                        piece=pawn,
                        start_square=pawn.position,
                        end_square=square,
                        taken_piece=self.board.get_piece_in_square(
                            Square(
                                row=Row(square.row - pawn.direction),
                                file=File(square.file),
                            )
                        ),
                    )
                    moves.add(move)
        return moves

    def _get_knight_moves(self, knight: Knight) -> set[Move]:
        moves = set()
        for row_delta, file_delta in knight.get_moves():
            square = create_and_validate_square(knight, row_delta, file_delta)
            if square:
                piece_in_square = self.board.get_piece_in_square(square)
                if piece_in_square and piece_in_square.color != knight.color:
                    move = Move(
                        piece=knight,
                        start_square=knight.position,
                        end_square=square,
                        taken_piece=piece_in_square,
                    )
                else:
                    move = Move(
                        piece=knight, start_square=knight.position, end_square=square
                    )
                moves.add(move)
        return moves

    def _get_king_moves(self, king: King) -> set[Move]:
        moves = set()
        for row_delta, file_delta in king.get_moves():
            square = create_and_validate_square(king, row_delta, file_delta)
            if square:
                piece_in_square = self.board.get_piece_in_square(square)
                if square not in self.attack_handler.get_attacked_squares():
                    if piece_in_square and piece_in_square.color != king.color:
                        move = Move(
                            piece=king,
                            start_square=king.position,
                            end_square=square,
                            taken_piece=piece_in_square,
                        )
                        moves.add(move)
                    if not piece_in_square:
                        move = Move(
                            piece=king,
                            start_square=king.position,
                            end_square=square,
                        )
                        moves.add(move)
        castling_moves = self._get_castling_moves(king)
        moves.update(castling_moves)
        return moves

    def _check_castle(
        self, rook_position: Square, squares: list[Square], king: King
    ) -> Move | None:
        rook = self.get_piece_by_position(rook_position, PieceType.ROOK)
        if rook and not rook.has_moved and rook.name == PieceType.ROOK:
            for square in squares:
                if square in self.attack_handler.get_attacked_squares():
                    return
                piece_in_square = self.board.get_piece_in_square(square)
                if piece_in_square:
                    return
            return Move(
                piece=king,
                start_square=king.position,
                end_square=squares[1],
            )

    def _get_castling_moves(self, king: King) -> set[Move]:
        moves = set()
        if king.has_moved:
            return moves
        if self.fen.move_order == Color.WHITE:
            short_castle = self._check_castle(
                rook_position=PositionsForCastlingWhite.short_rook,
                squares=PositionsForCastlingWhite.short_squares,
                king=king,
            )
            long_castle = self._check_castle(
                rook_position=PositionsForCastlingWhite.long_rook,
                squares=PositionsForCastlingWhite.long_squares,
                king=king,
            )
        else:
            short_castle = self._check_castle(
                rook_position=PositionsForCastlingBlack.short_rook,
                squares=PositionsForCastlingBlack.short_squares,
                king=king,
            )
            long_castle = self._check_castle(
                rook_position=PositionsForCastlingBlack.long_rook,
                squares=PositionsForCastlingBlack.long_squares,
                king=king,
            )
        if short_castle:
            moves.add(short_castle)
        if long_castle:
            moves.add(long_castle)
        return moves

    def _get_king(self, color: Color) -> King:
        for piece in self.pieces:
            if piece.name == PieceType.KING and piece.color == color:
                return piece

    def _get_opponent_color(self) -> Color:
        if self.fen.move_order == Color.WHITE:
            return Color.BLACK
        return Color.WHITE


class AttackHandler:
    def __init__(
        self, board: Board, opponent_color: Color, opponent_pieces: set[Piece]
    ):
        self.board = board
        self.opponent_color = opponent_color
        self.opponent_pieces = opponent_pieces
        self._cache: set[Square] = set()

    def get_attacked_squares(self) -> set[Square]:
        if self._cache:
            return self._cache
        self._cache = set()
        for piece in self.opponent_pieces:
            self._cache.update(self._get_piece_attacked_squares(piece))
        return self._cache

    def _get_piece_attacked_squares(self, piece: Piece) -> set[Square]:
        match piece:
            case Knight() | King():
                return self._get_king_and_knight_attacked_squares(piece)
            case Pawn():
                return self._get_pawn_attacked_squares(piece)
            case SlidingPiece():
                return self._get_sliding_pieces_attacked_squares(piece)

    @staticmethod
    def _get_king_and_knight_attacked_squares(piece: King | Knight) -> set[Square]:
        squares = set()
        for row_delta, file_delta in piece.get_moves():
            square = create_and_validate_square(piece, row_delta, file_delta)
            if square:
                squares.add(square)
        return squares

    @staticmethod
    def _get_pawn_attacked_squares(pawn: Pawn) -> set[Square]:
        squares = set()
        for side in (-1, 1):
            square = create_and_validate_square(pawn, pawn.direction, side)
            if square:
                squares.add(square)
        return squares

    def _get_sliding_pieces_attacked_squares(self, piece: SlidingPiece) -> set[Square]:
        squares = set()
        for ray in piece.get_moves():
            for row_delta, file_delta in ray:
                square = create_and_validate_square(piece, row_delta, file_delta)
                if square:
                    squares.add(square)
                    if self.board.get_piece_in_square(square):
                        break
        return squares
