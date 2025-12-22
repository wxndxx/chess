from app.handlers.board import Board
from app.handlers.position import PositionHandler, AttackHandler
from app.models import Move, PieceType

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

    def check_move(self, move: Move) -> tuple[Move | None, Board]:
        return self.make_a_move(move, False)

    def make_a_move(self, move: Move, save: bool = True) -> tuple[Move | None, Board]:
        taken_piece = self.board.make_move(move)
        if not self.is_legal(move):
            self.board.undo_move(move, taken_piece)
            return None, self.board
        temp_position = self._create_position(self.board, move)
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
        return move, self.board

    @staticmethod
    def _create_position(board: Board, move: Move) -> PositionHandler:
        move_order = get_next_color(move.side)
        position = PositionHandler(board=board, move_order=move_order, en_passant="-")
        return position
