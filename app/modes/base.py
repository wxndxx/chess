from app.configuration import Configuration
from app.handlers.board import Board
from app.handlers.fen import FEN
from app.handlers.pieces import PieceHandler
from app.handlers.position import PositionHandler
from app.handlers.search import SearchEngine, SearchResult


class BaseMode:
    def __init__(self) -> None:
        self.config = Configuration()
        self._board: Board = None
        self._position: PositionHandler = None
        self._search: SearchEngine = None
        self._search_result: SearchResult = None

    def _initialize(self, fen: FEN):
        pieces = PieceHandler.create_pieces(fen)
        self._board = Board(pieces)
        self._position = PositionHandler(
            board=self._board,
            move_order=fen.move_order,
            en_passant=fen.en_passant
        )
        self._search = SearchEngine(position=self._position)
