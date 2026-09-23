from app.game import Game
from app.models import Color


def main() -> Game:
    engine_color: Color | None = None
    while not engine_color:
        try:
            engine_color = Color(input("Enter the color of the engine (w/b):"))
        except ValueError as exc:
            print(exc)
    game = Game(engine_color)
    game.play()


if __name__ == "__main__":
    main()

