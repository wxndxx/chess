class FENParser:
    def __init__(self, data: str):
        self.__data = data
        self.position =

    def _parse(self):
        (
            self.position,
            self.move_order,
            self.castles,
            self.en_passant,
            self.draw_counter,
            self.move_counter,
        ) = self.__data.split(" ")
