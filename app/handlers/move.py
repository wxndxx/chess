from app.handlers.board import Board
from app.handlers.pieces import Pawn, Knight, Piece
from app.handlers.position import PositionHandler, AttackHandler
from app.models import Move, PieceType

from app.tools import get_next_color, create_and_validate_square


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
        taken_piece = self.board.make_move(move)
        if not self.is_legal(move):
            self.board.undo_move(move, taken_piece)
            return None, None
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
        return move, taken_piece

    @staticmethod
    def _create_position(board: Board, move: Move) -> PositionHandler:
        en_passant_square = None
        move_order = get_next_color(move.side)
        if move.piece == PieceType.PAWN:
            if abs(move.start_square.row - move.end_square.row) == 2:
                pawn: Pawn = board.get_piece_in_square(move.end_square)
                if isinstance(pawn, Knight):
                    print(f'ALARM! Move {move}')
                    board.display()
                en_passant_square = create_and_validate_square(
                    pawn, file_delta=0, row_delta=pawn.direction
                ).to_notation()
        position = PositionHandler(
            board=board, move_order=move_order, en_passant=en_passant_square
        )
        return position
