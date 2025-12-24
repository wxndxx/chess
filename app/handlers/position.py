from app.tools import create_and_validate_square
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
from app.handlers.pieces import Piece, SlidingPiece, Pawn, Knight, King


class PositionHandler:
    def __init__(self, board: Board, move_order: Color, en_passant: str, castling: str | None = None):
        self.board: Board = board
        self.move_order: Color = move_order
        self.en_passant: str | None = en_passant
        self.castling: str | None = castling
        opponent_color = self._get_opponent_color()
        self.attack_handler: AttackHandler = AttackHandler(
            board=self.board,
            opponent_color=opponent_color,
        )
        self._possible_moves: set[Move] = set()

    def is_check(self) -> bool:
        king = self.board.get_king(self.move_order)
        if king.position in self.attack_handler.get_attacked_squares():
            return True
        return False

    def is_mate(self) -> bool:
        king = self.board.get_king(self.move_order)
        king_moves = self._get_king_moves(king)
        if (
            king.position in self.attack_handler.get_attacked_squares()
            and len(king_moves) == 0
        ):
            return True
        return False

    def is_draw(self) -> bool:
        king = self.board.get_king(self.move_order)
        possible_moves = self.get_possible_moves()
        if (
            king not in self.attack_handler.get_attacked_squares()
            and len(possible_moves) == 0
        ):
            return True
        return False

    def get_possible_moves(self, color: Color | None = None) -> set[Move]:
        """Get all theoretical possible moves"""
        if not color:
            color = self.move_order
        if not self._possible_moves:
            pieces = self.board.get_pieces(color)
            for piece in pieces:
                self._possible_moves.update(self._get_piece_moves(piece))
        return self._possible_moves

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
                    if piece_in_square.color != piece.color and piece.name != PieceType.PAWN:
                        move = Move(
                            side=piece.color,
                            piece=piece.name,
                            start_square=piece.position,
                            end_square=square,
                            taken_piece=piece_in_square.name,
                            taken_piece_position=piece_in_square.position,
                        )
                        moves.add(move)
                    break
                else:
                    move = Move(
                        side=piece.color,
                        piece=piece.name, start_square=piece.position, end_square=square
                    )
                    moves.add(move)
        return moves

    @staticmethod
    def _is_last_rank(square: Square, direction: int) -> bool:
        if direction == -1:
            return square.row == 0
        return square.row == 7

    @staticmethod
    def _create_promotion_moves(pawn: Pawn, end_square: Square, piece_in_square: Piece | None = None) -> set[Move]:
        moves = set()
        for promotion in [PieceType.QUEEN, PieceType.KNIGHT, PieceType.ROOK, PieceType.BISHOP]:
            moves.add(Move(
                side=pawn.color,
                piece=pawn.name,
                start_square=pawn.position,
                end_square=end_square,
                taken_piece=piece_in_square.name if piece_in_square else None,
                taken_piece_position=piece_in_square.position if piece_in_square else None,
                promotion=promotion,
            ))
        return moves

    def _get_pawn_moves(self, pawn: Pawn) -> set[Move]:
        moves = self._get_sliding_piece_moves(pawn)
        if len(moves) == 1:
            move = next(iter(moves))
            if self._is_last_rank(move.end_square, pawn.direction):
                moves = self._create_promotion_moves(pawn, move.end_square)
        for side in (-1, 1):
            square = create_and_validate_square(pawn, pawn.direction, side)
            if square:
                piece_in_square = self.board.get_piece_in_square(square)
                if piece_in_square and piece_in_square.color != pawn.color:
                    if not self._is_last_rank(square, pawn.direction):
                        move = Move(
                            side=pawn.color,
                            piece=pawn.name,
                            start_square=pawn.position,
                            end_square=square,
                            taken_piece=piece_in_square.name,
                            taken_piece_position=piece_in_square.position,
                        )
                        moves.add(move)
                    else:
                        moves.update(self._create_promotion_moves(pawn, square, piece_in_square))
                if square.to_notation() == self.en_passant:
                    move = Move(
                        side=pawn.color,
                        piece=pawn.name,
                        start_square=pawn.position,
                        end_square=square,
                        taken_piece=PieceType.PAWN,
                        taken_piece_position=Square(
                            row=Row(square.row - pawn.direction),
                            file=File(square.file),
                        ),
                    )
                    moves.add(move)
        return moves

    def _get_knight_moves(self, knight: Knight) -> set[Move]:
        moves = set()
        move = None
        for row_delta, file_delta in knight.get_moves():
            square = create_and_validate_square(knight, row_delta, file_delta)
            if square:
                piece_in_square = self.board.get_piece_in_square(square)
                if piece_in_square and piece_in_square.color != knight.color:
                    move = Move(
                        side=knight.color,
                        piece=knight.name,
                        start_square=knight.position,
                        end_square=square,
                        taken_piece=piece_in_square.name,
                        taken_piece_position=piece_in_square.position,
                    )
                if not piece_in_square:
                    move = Move(
                        side=knight.color,
                        piece=knight.name,
                        start_square=knight.position,
                        end_square=square,
                    )
                if move:
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
                            side=king.color,
                            piece=king.name,
                            start_square=king.position,
                            end_square=square,
                            taken_piece=piece_in_square.name,
                            taken_piece_position=piece_in_square.position,
                        )
                        moves.add(move)
                    if not piece_in_square:
                        move = Move(
                            side=king.color,
                            piece=king.name,
                            start_square=king.position,
                            end_square=square,
                        )
                        moves.add(move)
        if not self.castling == "-":
            castling_moves = self.get_castling_moves(king)
            moves.update(castling_moves)
        return moves

    def _check_castle(
        self, rook_position: Square, squares: list[Square], king: King
    ) -> Move | None:
        rook = self.board.get_piece_in_square(rook_position)
        if rook and not rook.has_moved and rook.name == PieceType.ROOK:
            for square in squares:
                if square in self.attack_handler.get_attacked_squares():
                    return
                piece_in_square = self.board.get_piece_in_square(square)
                if piece_in_square:
                    return
            return Move(
                side=king.color,
                piece=king.name,
                start_square=king.position,
                end_square=squares[1],
            )

    def get_castling_moves(self, king: King) -> set[Move]:
        moves = set()
        if king.has_moved:
            return moves
        if self.move_order == Color.WHITE:
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

    def _get_opponent_color(self) -> Color:
        if self.move_order == Color.WHITE:
            return Color.BLACK
        return Color.WHITE


class AttackHandler:
    def __init__(self, board: Board, opponent_color: Color):
        self.board = board
        self.opponent_color = opponent_color
        self._cache: set[Square] = set()

    def get_attacked_squares(self) -> set[Square]:
        if self._cache:
            return self._cache
        self._cache = set()
        for piece in self.board.get_pieces(self.opponent_color):
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
                    piece_in_square = self.board.get_piece_in_square(square)
                    if piece_in_square and piece_in_square.name != PieceType.KING:
                        break
                    if piece_in_square and piece_in_square.color == piece.color:
                        break
        return squares
