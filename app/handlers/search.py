from dataclasses import dataclass, field

from app.handlers.evaluation import EvaluationHandler, PIECE_VALUES
from app.handlers.move import MoveHandler
from app.handlers.position import PositionHandler
from app.models import Move, Color
from app.tools import measure_time


INF = 40000
MATE_THRESHOLD = INF - 512


@dataclass
class SearchResult:
    score: int
    pv: list[Move] = field(default_factory=list)

    @property
    def move(self) -> Move | None:
        return self.pv[0] if self.pv else None

    def format_score(self) -> str:
        if self.score >= MATE_THRESHOLD:
            plies = INF - self.score
            return f"M{(plies + 1) // 2}"
        if self.score <= -MATE_THRESHOLD:
            plies = INF + self.score
            return f"-M{(plies + 1) // 2}"
        return f"{self.score / 100:.1f}"

    def format_line(self, side: Color, move_number: int = 1) -> str:
        if not self.pv:
            return ""
        parts: list[str] = []
        current = side
        number = move_number
        for index, move in enumerate(self.pv):
            if current == Color.WHITE:
                parts.append(f"{number}. {move}")
            elif index == 0:
                parts.append(f"{number}... {move}")
            else:
                parts.append(str(move))
            if current == Color.BLACK:
                number += 1
            current = Color.BLACK if current == Color.WHITE else Color.WHITE
        return " ".join(parts)

    def __str__(self) -> str:
        line = self.format_line(self.pv[0].side) if self.pv else ""
        if line:
            return f"{self.format_score()}  {line}"
        return self.format_score()


class SearchEngine:
    def __init__(self, position: PositionHandler):
        self.position = position
        self.evaluator = EvaluationHandler()
        self.board = position.board
        self.move_handler = MoveHandler(position.board)

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

    @measure_time
    def find_best_move(self, depth: int) -> SearchResult:
        alpha = -INF
        beta = INF
        best_pv: list[Move] = []

        for move in self._sort_moves(self.position.get_possible_moves()):
            final_move, taken_piece = self.move_handler.make_a_move(move)
            if not final_move:
                continue
            child_score, child_pv = self.search(
                depth=depth - 1,
                move=final_move,
                alpha=-beta,
                beta=-alpha,
                ply=1,
            )
            score = -child_score
            self.board.undo_move(final_move, taken_piece)
            if not best_pv or score > alpha:
                best_pv = [final_move] + child_pv
                if score > alpha:
                    alpha = score

            if alpha >= beta:
                break
        return SearchResult(score=alpha, pv=best_pv)

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
