from app.handlers.board import Board
from app.handlers.fen import FEN
from app.handlers.position import PositionHandler
from app.handlers.search import SearchEngine

fen = FEN("1nb1k1Br/3pQ2p/r1p3p1/p1B1p3/4P2N/2NP4/PPP2PPP/R4RK1 b - - 0 1")
board = Board(fen)
position = PositionHandler(fen=fen, board=board)
position.board.display()
search = SearchEngine(position=position)
print(f'Current move: {fen.move_order}')
print(f'Attacked squares: {position.attack_handler.get_attacked_squares()}')
print(f'Possible moves: {position.get_possible_moves()}')
print(f'Best move: {search.find_best_move()}')
