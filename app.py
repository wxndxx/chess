from app.handlers.board import Board
from app.handlers.pieces import PieceHandler
from app.handlers.position import PositionHandler
from app.handlers.search import SearchEngine
from app.configuration import Configuration


def main():
    config = Configuration()
    pieces = PieceHandler.create_pieces(config.fen)
    board = Board(pieces)
    board.display()
    position = PositionHandler(board=board, move_order=config.fen.move_order, en_passant=config.fen.en_passant)
    search = SearchEngine(position=position)
    result = search.find_best_move(config.depth)
    print(result.format_score())
    print(result.format_line(config.fen.move_order, config.fen.move_counter))


if __name__ == "__main__":
    main()

