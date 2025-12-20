from app.models import Color

NOTATION = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
REVERSE_NOTATION = {0: "a", 1: "b", 2: "c", 3: "d", 4: "e", 5: "f", 6: "g", 7: "h"}


class FEN:
    def __init__(
        self,
        fen_string: str | None = None,
        position: str = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR",
        move_order: Color = Color.WHITE,
        castles: str = "KQkq",
        en_passant: str = "-",
        draw_counter: int = 0,
        move_counter: int = 1,
    ):
        self.position = position
        self.move_order = move_order
        self.castles = castles
        self.en_passant = en_passant
        self.draw_counter = draw_counter
        self.move_counter = move_counter

        if fen_string:
            self._validate(fen_string)

    def __str__(self) -> str:
        return self._create_fen_string()

    def __repr__(self) -> str:
        return self._create_fen_string()

    def _validate(self, fen_string: str):
        raw_data = fen_string.split(" ")
        position = raw_data[0].split("/")
        assert len(raw_data) == 6
        assert len(position) == 8
        assert "k" in raw_data[0]
        assert "K" in raw_data[0]
        for row in position:
            if len(row) == 1:
                assert int(row[0]) == 8
            else:
                split = list(row)
                rows = 0
                for symbol in split:
                    if symbol.isdigit():
                        rows += int(symbol)
                    else:
                        rows += 1
                assert rows == 8

        self.position = raw_data[0]

        assert raw_data[1] in Color
        self.move_order = raw_data[1]

        for symbol in raw_data[2].lower():
            assert symbol in ["k", "q", "-"]
        self.castles = raw_data[2]

        self.en_passant = raw_data[3]
        self.draw_counter = int(raw_data[4])
        self.move_counter = int(raw_data[5])

    def show(self):
        return (
            f"{self.position} {self.move_order.value} {self.castles} "
            f"{self.en_passant} {self.draw_counter} {self.move_counter}"
        )

    def change_move_order(self):
        if self.move_order == Color.BLACK:
            self.move_order = Color.WHITE
        else:
            self.move_order = Color.BLACK

    def get_next_color(self):
        if self.move_order == Color.BLACK:
            return Color.WHITE
        return Color.BLACK

    def _create_fen_string(self) -> str:
        return (f"{self.position} {self.move_order.value} {self.castles} {self.en_passant} "
                f"{self.draw_counter} {self.move_counter}")
