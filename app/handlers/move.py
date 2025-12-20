from app.handlers.board import Board
from app.handlers.fen import FEN
from app.handlers.position import PositionHandler, AttackHandler
from app.models import Move, PieceType, Square, File, Color
from copy import deepcopy


class MoveHandler:
    def __init__(self, position: PositionHandler):
        self.initial_position = position

    @staticmethod
    def is_legal(move: Move, position: PositionHandler) -> bool:
        temp_board = deepcopy(position.board)
        king = temp_board.get_king(move.side)
        attacked_squares = AttackHandler(board=temp_board, opponent_color=position.fen.move_order).get_attacked_squares()
        return king.position not in attacked_squares

    @staticmethod
    def _move(move: Move, board: Board) -> Board:
        moved_piece = board.get_piece_in_square(move.start_square)
        if move.taken_piece:
            board.remove(move.taken_piece_position)
        moved_piece.position = move.end_square
        board.add(piece=moved_piece, square=move.end_square)
        board.remove(square=move.start_square)
        return board

    def make_a_move(self, move: Move) -> tuple[Move, PositionHandler] | None:
        check = False
        mate = False
        draw = False
        initial_board = deepcopy(self.initial_position.board)
        board = self._move(move, initial_board)
        new_position = self._create_position(board=board, move=move)
        if new_position.is_check():
            check = True
        if new_position.is_mate():
            mate = True
        if new_position.is_draw():
            draw = True
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
        )
        if self.is_legal(move, new_position):
            return move, new_position
        else:
            return None, None

    def _create_position(
        self, board: Board, move: Move
    ) -> PositionHandler:
        move_counter = self.initial_position.fen.move_counter + 1
        draw_counter = self.initial_position.fen.draw_counter
        move_order = self.initial_position.fen.get_next_color()

        if not move.taken_piece and not move.piece.name == PieceType.PAWN:
            draw_counter += 1

        if (
            move.piece.name == PieceType.PAWN
            and abs(move.end_square.row - move.start_square.row) == 2
        ):
            en_passant = Square(
                file=File(move.end_square.file),
                row=move.start_square.row + move.piece.direction,
            ).to_notation()
        else:
            en_passant = "-"

        fen = FEN(
            position=board.to_fen(),
            move_order=move_order,
            castles="",
            en_passant=en_passant,
            draw_counter=draw_counter,
            move_counter=move_counter,
        )
        temp_position = PositionHandler(fen=fen, board=board)
        for color in Color:
            king = temp_position.board.get_king(color)
            temp_position.get_castling_moves(king)
        return temp_position
