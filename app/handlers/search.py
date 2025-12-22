from app.handlers.evaluation import EvaluationHandler
from app.handlers.move import MoveHandler
from app.handlers.position import PositionHandler
from app.models import Move, Color


class SearchEngine:
    def __init__(self, position: PositionHandler):
        self.position = position
        self.evaluator = EvaluationHandler()

    def search(self, position, depth):
        if position.is_mate():
            return 20000 if position.fen.move_order == Color.WHITE else -20000
        if position.is_draw():
            return 0
        if depth == 0:
            return self.evaluator.evaluate(position)

        best = -20000
        for move in position.get_possible_moves():
            move_handler = MoveHandler(position)
            _, new_pos = move_handler.make_a_move(move)
            if new_pos:
                score = -self.search(new_pos, depth - 1)
                best = max(best, score)
        return best

    def find_best_move(self, depth: int) -> tuple[Move, int]:
        best_move: Move | None = None
        best_score = -20000
        color_sign = 1 if self.position.move_order == Color.WHITE else -1

        move_handler = MoveHandler(self.position)
        for move in self.position.get_possible_moves():
            final_move, new_position = move_handler.make_a_move(move)
            if final_move and new_position:
                print(f'Checking move {final_move}')
                if final_move.mate:
                    return final_move, best_score
                score = -self.search(new_position, depth=depth) * color_sign

                if score > best_score:
                    best_score = score
                    best_move = final_move

        return best_move, best_score
