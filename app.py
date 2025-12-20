from app.handlers.fen import FEN
from app.handlers.position import Position

fen = FEN("rnbqkb1r/pppp1ppp/5n2/4p3/4PP2/2N5/PPPP2PP/R1BQKBNR b KQkq f3 0 1")
position = Position(fen=fen)
position.board.display()
print(f'Current move: {fen.move_order}')
print(f'Attacked squares: {position.attack_handler.get_attacked_squares()}')
print(f'Possible moves: {position.get_possible_moves()}')

