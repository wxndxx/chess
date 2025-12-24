from app.handlers.board import Board
from app.handlers.evaluation import EvaluationHandler
from app.handlers.fen import FEN
from app.handlers.pieces import PieceHandler
from app.handlers.position import PositionHandler
from app.handlers.search import SearchEngine


def main(depth: int):
    fen = FEN("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
    pieces = PieceHandler.create_pieces(fen)
    board = Board(pieces)
    board.display()
    position = PositionHandler(board=board, move_order=fen.move_order, en_passant=fen.en_passant)
    search = SearchEngine(position=position)
    print(f'Current move: {fen.move_order}')
    print(f'Attacked squares: {position.attack_handler.get_attacked_squares()}')
    print(f'Possible moves: {position.get_possible_moves()}')
    score = EvaluationHandler().evaluate(position=position)
    print(f'Score: {score}')
    best_move, best_score = search.find_best_move(depth)
    print(f'Best move: {best_move} with score {best_score}')


if __name__ == "__main__":
    main(4)

