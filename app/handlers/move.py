from app.handlers.board import Board
from app.handlers.pieces import Piece
from app.handlers.position import PositionHandler, AttackHandler
from app.models import Move, PieceType, Square, Row

from app.tools import get_next_color


class MoveHandler:
    def __init__(self, board: Board):
        self.board = board

    def is_legal(self, move: Move) -> bool:
        king = self.board.get_king(move.side)
        attacked_squares = AttackHandler(
            board=self.board, opponent_color=get_next_color(move.side)
        ).get_attacked_squares()
        return king.position not in attacked_squares

    def check_move(self, move: Move) -> tuple[Move | None, Piece | None]:
        return self.make_a_move(move, save=False)

    def make_a_move(self, move: Move, save: bool = True) -> tuple[Move | None, Piece | None]:
        if self.board.get_piece_in_square(move.start_square) is None:
            return None, None
        taken_piece = self.board.make_move(move)
        if not self.is_legal(move):
            self.board.undo_move(move, taken_piece)
            return None, None
        temp_position = self.position_after(move)
        check = temp_position.is_check()
        mate = temp_position.is_mate()
        draw = temp_position.is_draw()
        move = Move(
            side=move.side,
            piece=move.piece,
            start_square=move.start_square,
            end_square=move.end_square,
            taken_piece=move.taken_piece,
            taken_piece_position=move.taken_piece_position,
            check=check,
            mate=mate,
            draw=draw,
            promotion=move.promotion,
        )
        if not save:
            self.board.undo_move(move, taken_piece)
        return move, taken_piece

    def position_after(self, move: Move) -> PositionHandler:
        return PositionHandler(
            board=self.board,
            move_order=get_next_color(move.side),
            en_passant=self._en_passant_after(move),
        )

    @staticmethod
    def _en_passant_after(move: Move) -> str:
        if move.piece != PieceType.PAWN:
            return "-"
        if abs(move.start_square.row - move.end_square.row) != 2:
            return "-"
        skipped = Square(
            row=Row((move.start_square.row + move.end_square.row) // 2),
            file=move.end_square.file,
        )
        return skipped.to_notation()
