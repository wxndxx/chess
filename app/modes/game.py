from app.models import Color, Move
from app.modes.base import BaseMode


class Game(BaseMode):
    def __init__(self, color: Color, pretty: bool, icons: bool, score: bool) -> None:
        super().__init__()
        self.pretty = pretty
        self.icons = icons
        self.score = score
        self.color = color

        self._initialize(self.config.fen)

    def show_board(self) -> None:
        self._board.display(self.pretty, self.icons)

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

    def loop(self) -> None:
        try:
            while True:
                self.show_board()
                if self.score and self._search_result is not None:
                    print(f"Score: {round(self._search_result.score / 100, 1)}\n"
                          f"PV: {self._search_result.pv_fen}")

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
        except KeyboardInterrupt:
            print("\nThank you for playing!")
