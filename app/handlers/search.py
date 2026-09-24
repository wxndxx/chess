import time
from dataclasses import dataclass, field

from app.handlers.evaluation import EvaluationHandler, PIECE_VALUES
from app.handlers.move import MoveHandler
from app.handlers.position import PositionHandler
from app.models import Move, Color, SearchResult
from app.tools import measure_time


INF = 40000
MATE_THRESHOLD = INF - 512


class SearchEngine:
    def __init__(self, position: PositionHandler):
        self.position = position
        self.evaluator = EvaluationHandler()
        self.board = position.board
        self.move_handler = MoveHandler(position.board)
        self.nodes: int = 0

    def _evaluate(self, position: PositionHandler) -> int:
        score = self.evaluator.evaluate(position)
        if position.move_order == Color.BLACK:
            return -score
        return score

    def _position_after(self, move: Move) -> PositionHandler:
        return self.move_handler.position_after(move)

    def quiescence(
        self,
        position: PositionHandler,
        alpha: int,
        beta: int,
        depth: int = 0,
        ply: int = 0,
    ) -> tuple[int, list[Move]]:
        self.nodes += 1
        if position.is_mate():
            return -INF + ply, []
        if position.is_draw():
            return 0, []
        stand_pat = self._evaluate(position)
        if depth >= 8:
            return stand_pat, []
        if stand_pat >= beta:
            return beta, []
        if stand_pat > alpha:
            alpha = stand_pat
        best_pv: list[Move] = []
        for move in self._sort_moves(position.get_possible_moves()):
            if not move.taken_piece:
                continue
            new_move, taken_piece = self.move_handler.make_a_move(move)
            if not new_move:
                continue
            next_position = self._position_after(new_move)
            child_score, child_pv = self.quiescence(
                next_position, -beta, -alpha, depth + 1, ply + 1
            )
            score = -child_score
            self.board.undo_move(new_move, taken_piece)
            if score >= beta:
                return beta, [new_move] + child_pv
            if not best_pv or score > alpha:
                best_pv = [new_move] + child_pv
                if score > alpha:
                    alpha = score
        return alpha, best_pv

    def search(
        self, depth: int, move: Move, alpha: int, beta: int, ply: int
    ) -> tuple[int, list[Move]]:
        self.nodes += 1
        position = self._position_after(move)
        if move.mate:
            return -INF + ply, []
        if move.draw:
            return 0, []
        if depth == 0:
            return self.quiescence(position, alpha, beta, ply=ply)

        best_pv: list[Move] = []
        had_legal = False
        for nested_move in self._sort_moves(position.get_possible_moves()):
            new_move, taken_piece = self.move_handler.make_a_move(nested_move)
            if not new_move:
                continue
            had_legal = True
            child_score, child_pv = self.search(
                depth - 1,
                new_move,
                -beta,
                -alpha,
                ply + 1,
            )
            score = -child_score
            self.board.undo_move(new_move, taken_piece)
            if not best_pv or score > alpha:
                best_pv = [new_move] + child_pv
                if score > alpha:
                    alpha = score
            if alpha >= beta:
                break
        if not had_legal:
            terminal = -INF + ply if position.is_check() else 0
            return terminal, []
        return alpha, best_pv

    def find_best_move(self, depth: int) -> SearchResult:
        alpha = -INF
        beta = INF
        best_pv: list[Move] = []
        self.nodes = 1
        start = time.perf_counter()

        for move in self._sort_moves(self.position.get_possible_moves()):
            final_move, taken_piece = self.move_handler.make_a_move(move)
            if not final_move:
                continue
            child_score, child_pv = self.search(
                depth=depth - 1,
                move=final_move,
                alpha=-beta,
                beta=-alpha,
                ply=1
            )
            score = -child_score
            self.board.undo_move(final_move, taken_piece)
            if not best_pv or score > alpha:
                best_pv = [final_move] + child_pv
                if score > alpha:
                    alpha = score

            if alpha >= beta:
                break

        elapsed = int((time.perf_counter() - start) * 1000)
        return SearchResult(score=alpha, move_line=best_pv, nodes=self.nodes, time=elapsed)

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
