from pieces import PieceFactory, Piece, Position, Color


DEFAULT_START_POSITION = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"


class Singleton:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Singleton, cls).__new__(cls)
            return cls._instance


class Board(Singleton):
    def __init__(self) -> None:
        self.board = [[], [], [], [], [], [], [], []]  # row[file]
        self.notation = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}
        self.reverse_notation = {0: 'a', 1: 'b', 2: 'c', 3: 'd', 4: 'e', 5: 'f', 6: 'g', 7: 'h'}

    def __repr__(self) -> str:
        return str(self.board)

    def initialize(self, start_position: str = DEFAULT_START_POSITION) -> tuple[list, list]:
        black_pieces = []
        white_pieces = []
        row_index = 7
        for row in start_position.split("/"):
            file_index = 0
            for x in row:
                if x.isdigit():
                    for i in range(int(x)):
                        self.board[row_index].append("-")
                else:
                    piece = PieceFactory.get_piece(symbol=x, position=Position(row=row_index, file=file_index))
                    white_pieces.append(piece) if piece.color == Color.WHITE else black_pieces.append(piece)
                    self.board[row_index].append(piece)
                file_index += 1
            row_index -= 1
        return white_pieces, black_pieces

    def _get_index_by_notation(self, notation: str) -> Position:
        x, y = list(notation)
        return Position(file=self.notation[x], row=int(y) - 1)

    def get_square(self, notation: str) -> Piece | str:
        index = self._get_index_by_notation(notation)
        return self.board[index.row][index.file]

    def get_square_by_index(self, position: Position) -> Piece | str:
        return self.board[position.row][position.file]

    @property
    def display(self) -> list[str]:
        return [(
            f"8 | {self.board[7][0]} {self.board[7][1]} {self.board[7][2]} {self.board[7][3]} {self.board[7][4]} "
            f"{self.board[7][5]} {self.board[7][6]} {self.board[7][7]}"
        ),
        (
            f"7 | {self.board[6][0]} {self.board[6][1]} {self.board[6][2]} {self.board[6][3]} {self.board[6][4]} "
            f"{self.board[6][5]} {self.board[6][6]} {self.board[6][7]} "
        ),
        (
            f"6 | {self.board[5][0]} {self.board[5][1]} {self.board[5][2]} {self.board[5][3]} {self.board[5][4]} "
            f"{self.board[5][5]} {self.board[5][6]} {self.board[5][7]} "
        ),
        (
            f"5 | {self.board[4][0]} {self.board[4][1]} {self.board[4][2]} {self.board[4][3]} {self.board[4][4]} "
            f"{self.board[4][5]} {self.board[4][6]} {self.board[4][7]} "
        ),
        (
            f"4 | {self.board[3][0]} {self.board[3][1]} {self.board[3][2]} {self.board[3][3]} {self.board[3][4]} "
            f"{self.board[3][5]} {self.board[3][6]} {self.board[3][7]} "
        ),
        (
            f"3 | {self.board[2][0]} {self.board[2][1]} {self.board[2][2]} {self.board[2][3]} {self.board[2][4]} "
            f"{self.board[2][5]} {self.board[2][6]} {self.board[2][7]} "
        ),
        (
            f"2 | {self.board[1][0]} {self.board[1][1]} {self.board[1][2]} {self.board[1][3]} {self.board[1][4]} "
            f"{self.board[1][5]} {self.board[1][6]} {self.board[1][7]} "
        ),
        (
            f"1 | {self.board[0][0]} {self.board[0][1]} {self.board[0][2]} {self.board[0][3]} {self.board[0][4]} "
            f"{self.board[0][5]} {self.board[0][6]} {self.board[0][7]} "
        ), '____________________', '  | a b c d e f g h']

    @property
    def fen(self) -> str:
        result = []
        for row_index in range(7, -1, -1):
            row = []
            for x in self.board[row_index]:
                if x == "-":
                    if len(row) > 0 and isinstance(row[-1], int):
                        row[-1] += 1
                    else:
                        row.append(1)
                else:
                    if len(row) > 0 and isinstance(row[-1], int):
                        row[-1] = str(row[-1])
                    row.append(str(x))
            if isinstance(row[-1], int):
                row[-1] = str(row[-1])
            result.append("".join(row))
        return "/".join(result)
