import sys
from datetime import datetime


class StreamLog:
    def __init__(self, stream, log, name: str) -> None:
        self._stream = stream
        self._log = log
        self._name = name

    def write(self, data: str) -> int:
        if data:
            self._log.write(f"{self._name} {data}")
            self._log.flush()
        self._stream.write(data)
        self._stream.flush()
        return len(data)

    def readline(self, size: int = -1) -> str:
        line = self._stream.readline(size)
        if line:
            self._log.write(f"{self._name} {line}")
            self._log.flush()
        return line

    def flush(self) -> None:
        self._stream.flush()

    def __getattr__(self, name: str):
        return getattr(self._stream, name)


def debug() -> None:
    date = datetime.now().strftime("%m-%d-%Y_%H-%M")
    filename = f"engine_{date}.log"
    log = open(filename, "a", encoding="utf-8", buffering=1)
    sys.stdin = StreamLog(sys.stdin, log, "<<")
    sys.stdout = StreamLog(sys.stdout, log, ">>")
    sys.stderr = StreamLog(sys.stderr, log, "!!")
