from app.configuration import Configuration
from app.handlers.board import Board
from app.handlers.pieces import PieceHandler
from app.handlers.position import PositionHandler
from app.handlers.search import SearchEngine, SearchResult
from app.models import Color, Move


class Game:
    def __init__(self, color: Color, pretty: bool, score: bool) -> None:
        self.pretty = pretty
        self.score = score
        self.config = Configuration()
        self.color = color
        self._board: Board = None
        self._position: PositionHandler = None
        self._search: SearchEngine = None
        self._search_result: SearchResult = None

        self._initialize()

    def _initialize(self):
        pieces = PieceHandler.create_pieces(self.config.fen)
        self._board = Board(pieces)
        self._position = PositionHandler(
            board=self._board,
            move_order=self.config.fen.move_order,
            en_passant=self.config.fen.en_passant
        )
        self._search = SearchEngine(position=self._position)

    def show_board(self) -> None:
        self._board.display(self.pretty)

    def parse_user_move(self) -> Move:
        user_move = None
        while user_move is None:
            text = input("Enter your move: ").strip()
            for move in self._position.get_possible_moves():
                if text == str(move):
                    user_move, _ = self._search.move_handler.make_a_move(move)
                    if user_move:
                        break
            if not user_move:
                print(f"Invalid move - {text}. Possible moves - {self._position.get_possible_moves()}")
        return user_move

    def play(self) -> None:
        while True:
            self.show_board()
            if self.score and self._search_result is not None:
                print(f"Score: {self._search_result.format_score()}")
            if self._position.is_mate() or self._position.is_draw():
                break
            if self._position.move_order == self.color:
                print("Thinking...")
                self._search_result = self._search.find_best_move(self.config.depth)
                played, _ = self._search.move_handler.make_a_move(self._search_result.move)
                print(played)
            else:
                played = self.parse_user_move()

            self._position = self._search.move_handler.position_after(played)
            self._search.position = self._position

