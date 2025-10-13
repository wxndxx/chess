from board import Board
from pieces import Piece

DEFAULT_START_POSITION = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"


class Engine:
    def __init__(self):
        self.move_order = None
        self.castles = None
        self.en_passant = None
        self.draw_counter = None
        self.move_counter = 1
        self.board = Board()
        self.black_pieces = []
        self.white_pieces = []

    def initialize(self, start_position: str):
        self._parse_start_position(start_position)

    def get_piece_moves(self, piece: Piece):
        possible_moves = piece.get_possible_moves()
        result = []
        for move in possible_moves:
            square = self.board.get_square_by_index(move)
            if isinstance(square, Piece):
                if square.color == piece.color:
                    pass
            else:
                result.append(move)
        return result

    def _parse_start_position(self, start_position: str):
        (
            raw_position,
            self.move_order,
            self.castles,
            self.en_passant,
            self.draw_counter,
            self.move_counter,
        ) = start_position.split(" ")
        self.white_pieces, self.black_pieces = self.board.initialize(raw_position)

    @property
    def fen(self) -> str:
        return (f'{self.board.fen} {self.move_order} {self.castles} {self.en_passant} {self.draw_counter} '
                f'{self.move_counter}')


e = Engine()
e.initialize(DEFAULT_START_POSITION)
for row in e.board.display:
    print(row)
