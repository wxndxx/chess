from app.handlers.fen import FEN


class Configuration:
    def __init__(self) -> None:
        self._fen = None
        self._depth = None

        self._from_file()

    @property
    def fen(self) -> FEN:
        return self._fen

    @property
    def depth(self) -> int:
        return self._depth

    def _from_file(self) -> None:
        with open(".env", "r") as file:
            for line in file:
                parsed_line = line.strip().split("=")
                if len(parsed_line) != 2:
                    raise ValueError("Invalid configuration file", line)
                if parsed_line[0].lower() == "fen":
                    self._fen = FEN(fen_string=parsed_line[1][1:-1])
                if parsed_line[0].lower() == "depth":
                    self._depth = int(parsed_line[1])
