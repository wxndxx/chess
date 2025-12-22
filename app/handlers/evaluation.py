from app.handlers.position import PositionHandler, AttackHandler
from app.handlers.pst import piece_square_value
from app.models import PieceType, Color

PIECE_VALUES = {
    PieceType.PAWN: 100,
    PieceType.KNIGHT: 320,
    PieceType.BISHOP: 330,
    PieceType.ROOK: 500,
    PieceType.QUEEN: 900,
    PieceType.KING: 0,
}


class EvaluationHandler:

    @classmethod
    def evaluate(cls, position: PositionHandler) -> int:
        if position.is_mate():
            return -10000 if position.move_order == Color.WHITE else 10000

        if position.is_draw():
            return 0

        score = 0

        score += cls._material(position)
        score += cls._mobility(position)
        score += cls._king_safety(position)

        return score

    @staticmethod
    def _material(position: PositionHandler) -> int:
        score = 0
        for piece in position.board.get_all_pieces():
            value = PIECE_VALUES[piece.name]
            pst_bonus = piece_square_value(piece)
            score += value + pst_bonus if piece.color == Color.WHITE else -value + pst_bonus
        return score

    @staticmethod
    def _mobility(position: PositionHandler) -> int:
        white_moves = len(position.get_possible_moves(Color.WHITE))
        black_moves = len(position.get_possible_moves(Color.BLACK))
        return (white_moves - black_moves) * 2

    @staticmethod
    def _king_safety(position: PositionHandler) -> int:
        score = 0

        for color in (Color.WHITE, Color.BLACK):
            king = position.board.get_king(color)
            opponent_color = Color.BLACK if color == Color.WHITE else Color.WHITE
            attacked = AttackHandler(position.board, opponent_color).get_attacked_squares()
            danger = sum(
                1 for sq in attacked
                if abs(sq.row - king.position.row) <= 1
                and abs(sq.file - king.position.file) <= 1
            )

            score += -danger * 20 if color == Color.WHITE else danger * 20
        return score
