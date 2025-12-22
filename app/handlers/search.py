from app.handlers.evaluation import EvaluationHandler
from app.handlers.move import MoveHandler
from app.handlers.position import PositionHandler
from app.models import Move, Color


class SearchEngine:
    def __init__(self, position: PositionHandler):
        self.position = position
        self.evaluator = EvaluationHandler()

    def find_best_move(self) -> Move:
        best_move: Move | None = None
        best_score = -float("inf")
        color_sign = 1 if self.position.fen.move_order == Color.WHITE else -1

        move_handler = MoveHandler(self.position)
        for move in self.position.get_possible_moves():
            final_move, new_position = move_handler.make_a_move(move)
            if final_move and new_position:
                if final_move.mate:
                    return final_move
                score = color_sign * self.evaluator.evaluate(new_position)

                if score > best_score:
                    best_score = score
                    best_move = final_move

        return best_move

