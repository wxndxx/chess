import sys

from app.exceptions import InvalidCommandException
from app.handlers.fen import FEN
from app.models import AUTHOR, NAME, UCICommands, Color, Move, PieceType
from app.modes.base import BaseMode
from app.tools import notation_to_square


class UciEngine(BaseMode):
    def __init__(self):
        super().__init__()
        self.depth: int = 3

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
        if "moves" in command:
            index = command.index("moves")
            for raw_move in command[index + 1:]:
                move = self._uci_move(raw_move)
                played, _ = self._search.move_handler.make_a_move(move)
                if played is None:
                    raise InvalidCommandException(raw_move)
                self._position = self._search.move_handler.position_after(played)
                self._search.position = self._position
        else:
            raise InvalidCommandException(command)

    def _go(self, params: list) -> None:
        if len(params) < 2:
            raise InvalidCommandException(params, "Incorrect number of arguments")
        if params[1] == "depth":
            self.depth = int(params[2])
        self._search_result = self._search.find_best_move(self.depth)
        self._info(
            score=self._search_result.score,
            nodes=self._search_result.nodes,
            time=self._search_result.time,
            pv=self._search_result.pv
        )
        played, _ = self._search.move_handler.make_a_move(self._search_result.move)
        if played:
            print(f"bestmove {str(played.start_square) + str(played.end_square)}")
        else:
            print(f"bestmove (none)")

    def _uci_move(self, raw_move: str) -> Move:
        start = notation_to_square(raw_move[:2])
        end = notation_to_square(raw_move[2:4])
        promotion = PieceType(raw_move[4]) if len(raw_move) == 5 else None
        for move in self._position.get_possible_moves():
            if (
                    move.start_square == start
                    and move.end_square == end
                    and move.promotion == promotion
            ):
                return move
        raise InvalidCommandException(raw_move, "Invalid move")

    def _info(self, score: int, nodes: int, time: int, pv: str) -> None:
        print(f"info depth {self.depth} score cp {score} nodes {nodes} time {time} pv {pv}")

    def _identify(self) -> None:
        self._send(f"id name {NAME}")
        self._send(f"id author {AUTHOR}")
        self._send("uciok")

    def _ready(self) -> None:
        self._send("readyok")

