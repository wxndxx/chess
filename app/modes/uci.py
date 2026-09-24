import sys

from app.exceptions import InvalidCommandException
from app.handlers.fen import FEN
from app.models import AUTHOR, NAME, UCICommands, Color
from app.modes.base import BaseMode


class UciEngine(BaseMode):

    @staticmethod
    def _send(message: str) -> None:
        print(message, flush=True)

    def loop(self) -> None:
        self._identify()
        while True:
            line = sys.stdin.readline()
            if not line:
                break
            parts = line.strip().split()
            if not parts:
                continue
            raw = parts[0]
            try:
                command = UCICommands(raw)
                match command:
                    case UCICommands.UCI:
                        self._identify()
                    case UCICommands.READY:
                        self._ready()
                    case UCICommands.POSITION:
                        self._create_position(command=parts)
                    case UCICommands.NEW_GAME:
                        pass
                    case UCICommands.GO:
                        self._go(params=parts)
                    case UCICommands.QUIT:
                        break
            except (ValueError, InvalidCommandException) as exc:
                print(exc)

    def _create_position(self, command: list) -> None:
        """
        position [fen <fenstring> | startpos ]  moves <move1> .... <movei>
        """
        if len(command) < 2:
            raise InvalidCommandException(command)
        if command[1] == "fen":
            if len(command) < 7:
                raise InvalidCommandException(command, "Incorrect number of arguments")
            fen = FEN(
                position=command[2],
                move_order=Color(command[3]),
                castles=command[4],
                en_passant=command[5],
                draw_counter=command[6],
                move_counter=command[7],
            )
            self._initialize(fen)
        elif command[1] == "startpos":
            self._initialize(FEN())
        else:
            raise InvalidCommandException(command)

    def _go(self, params: list) -> None:
        if len(params) < 2:
            raise InvalidCommandException(params, "Incorrect number of arguments")
        if params[1] == "depth":
            depth = int(params[2])
            print(f"info depth {depth}")
            self._search_result = self._search.find_best_move.__wrapped__(self._search, depth)
            played, _ = self._search.move_handler.make_a_move(self._search_result.move)
            if played:
                print(f"bestmove {str(played.start_square) + str(played.end_square)}")
            else:
                print(f"bestmove (none)")

    def _identify(self) -> None:
        self._send(f"id name {NAME}")
        self._send(f"id author {AUTHOR}")
        self._send("uciok")

    def _ready(self) -> None:
        self._send("readyok")

