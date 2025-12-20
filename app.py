from app.handlers.board import Board
from app.handlers.fen import FEN
from app.handlers.move import MoveHandler
from app.handlers.position import PositionHandler

fen = FEN("k7/8/1Q6/7p/7P/8/8/1K6 b - - 0 1")
board = Board(fen)
position = PositionHandler(fen=fen, board=board)
position.board.display()
print(f'Current move: {fen.move_order}')
print(f'Attacked squares: {position.attack_handler.get_attacked_squares()}')
print(f'Possible moves: {position.get_possible_moves()}')

# move_handler = MoveHandler(position)
# for move in position.get_possible_moves():
#     if move.to_fen() == 'dxe6':
#         final_move, new_position = move_handler.make_a_move(move)
#
# print(f'Move: {final_move.to_fen()}')
# print(f'Possible moves: {new_position.get_possible_moves()}')