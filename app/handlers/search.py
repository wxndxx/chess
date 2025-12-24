import os

from app.handlers.evaluation import EvaluationHandler, PIECE_VALUES
from app.handlers.move import MoveHandler
from app.handlers.position import PositionHandler
from app.models import Move, Color
from app.tools import get_next_color, measure_time


INF = 40000


class SearchEngine:
    def __init__(self, position: PositionHandler):
        self.position = position
        self.evaluator = EvaluationHandler()
        self.board = position.board
        self.move_handler = MoveHandler(position.board)

    def quiescence(self, alpha: int, beta: int, depth: int = 0) -> int:
        stand_pat = self.evaluator.evaluate(self.position)
        if depth >= 8:
            return stand_pat
        if stand_pat >= beta:
            return beta
        if stand_pat > alpha:
            alpha = stand_pat
        for move in self._sort_moves(self.position.get_possible_moves()):
            if not (move.taken_piece or move.check):
                continue
            new_move, taken_piece = self.move_handler.make_a_move(move)
            if not new_move:
                continue
            score = -self.quiescence(-beta, -alpha, depth + 1)
            self.board.undo_move(new_move, taken_piece)
            if score >= beta:
                return beta
            if score > alpha:
                alpha = score
        return alpha

    def search(self, depth: int, move: Move, alpha: int, beta: int) -> int:
        if move.mate:
            return INF
        if move.draw:
            return 0
        new_move_order = get_next_color(move.side)
        position = PositionHandler(self.board, new_move_order, en_passant="-")
        if depth == 0:
            return self.quiescence(alpha, beta)
        for nested_move in self._sort_moves(position.get_possible_moves()):
            new_move, taken_piece = self.move_handler.make_a_move(nested_move)
            if not new_move:
                continue
            score = -self.search(
                depth - 1,
                new_move,
                -beta,
                -alpha,
            )
            self.board.undo_move(new_move, taken_piece)
            if score > alpha:
                alpha = score
            if alpha >= beta:
                break
        return alpha

    @measure_time
    def find_best_move(self, depth: int) -> tuple[Move, int]:
        best_move: Move | None = None
        alpha = -INF
        beta = INF

        for move in self._sort_moves(self.position.get_possible_moves()):
            final_move, taken_piece = self.move_handler.make_a_move(move)
            if not final_move:
                continue
            if final_move.mate:
                self.board.undo_move(final_move, taken_piece)
                return final_move, INF
            score = -self.search(
                depth=depth - 1,
                move=final_move,
                alpha=-beta,
                beta=-alpha,
            )
            self.board.undo_move(final_move, taken_piece)
            if score > alpha:
                alpha = score
                best_move = final_move

            if alpha >= beta:
                break
        return best_move, alpha

    @staticmethod
    def _sort_moves(moves: set[Move]) -> list[Move]:
        return sorted(
            moves,
            key=lambda m: (
                not m.mate,
                not m.check,
                not bool(m.taken_piece),
                -PIECE_VALUES.get(m.taken_piece, 0),
                PIECE_VALUES[m.piece],
            )
        )
