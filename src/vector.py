class Vector:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def to_list(self) -> list[int, int]:
        return [self.x, self.y]
