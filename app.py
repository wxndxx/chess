from app.handlers.board import Board
from app.handlers.evaluation import EvaluationHandler
from app.handlers.fen import FEN
from app.handlers.pieces import PieceHandler
from app.handlers.position import PositionHandler
from app.handlers.search import SearchEngine

fen = FEN("rnbqkbnr/pppp1ppp/8/4p3/2P5/8/PP1PPPPP/RNBQKBNR w KQkq e6 0 1")
pieces = PieceHandler.create_pieces(fen)
board = Board(pieces)
position = PositionHandler(board=board, move_order=fen.move_order, en_passant=fen.en_passant)
position.board.display()
search = SearchEngine(position=position)
print(f'Current move: {fen.move_order}')
print(f'Attacked squares: {position.attack_handler.get_attacked_squares()}')
print(f'Possible moves: {position.get_possible_moves()}')
score = EvaluationHandler().evaluate(position=position)
print(f'Score: {score}')
# RESULT = search.find_best_move(2)
# print(RESULT)
# best_move, best_score = RESULT
# print(f'Best move: {best_move} with score {best_score}')
