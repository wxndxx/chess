from app.game import Game
from app.models import Color


def _question(text: str) -> bool:
    statement: bool | None = None
    while statement is None:
        answer = input(f"{text} (y/n): ")
        if answer == "y":
            statement = True
        elif answer == "n":
            statement = False
        else:
            print("Please enter 'y' or 'n'")
    return statement


def main() -> Game:
    engine_color: Color | None = None
    while not engine_color:
        try:
            engine_color = Color(input("Enter the color of the engine (w/b):"))
        except ValueError as exc:
            print(exc)

    pretty = _question("Do you want a board to be pretty")
    icons = _question("Do you want to use icons of the pieces")
    score = _question("Do you want to see a computer evaluation")

    game = Game(engine_color, pretty=pretty, icons=icons, score=score)
    game.play()


if __name__ == "__main__":
    main()

