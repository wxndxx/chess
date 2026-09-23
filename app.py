from app.game import Game
from app.models import Color


def main() -> Game:
    engine_color: Color | None = None
    while not engine_color:
        try:
            engine_color = Color(input("Enter the color of the engine (w/b):"))
        except ValueError as exc:
            print(exc)
    pretty: bool | None = None
    while pretty is None:
        answer = input("Do you want a board to be pretty (y/n): ")
        if answer == "y":
            pretty = True
        elif answer == "n":
            pretty = False
        else:
            print("Please enter 'y' or 'n'")
    score: bool | None = None
    while score is None:
        answer = input("Do you want to see a computer evaluation (y/n): ")
        if answer == "y":
            score = True
        elif answer == "n":
            score = False
        else:
            print("Please enter 'y' or 'n'")

    game = Game(engine_color, pretty=pretty, score=score)
    game.play()


if __name__ == "__main__":
    main()

