from abc import ABC, abstractmethod

from core import Cell, CellType


class Ship(ABC):
    def __init__(self, x: int, y: int):  # left top corner
        self.x = x
        self.y = y

    @abstractmethod
    def get_matrix(self) -> list[list[int]]:
        pass

    # def rotate(self):
    #     self.matrix = list(zip(*self.matrix[::-1]))

    def point_inside(self, x: int, y: int) -> bool:
        return self.x <= x < self.x + len(self.get_matrix()[0]) and self.y <= y < self.y + len(self.get_matrix())

    def get_occupied_cells(self) -> list[Cell]:
        cells = []
        for y, row in enumerate(self.get_matrix()):
            for x, cell in enumerate(row):
                if cell == 1:
                    cells.append(Cell(self.x + x, self.y + y, CellType.SHIP_HIT))
        return cells

    def get_surrounding_cells(self) -> list[Cell]:
        cells = []
        m = self.get_matrix()
        for x in range(-1, len(m[0]) + 1):
            for y in range(-1, len(m) + 1):
                if 0 <= y < len(m) and 0 <= x < len(m[0]) and m[y][x] == 1:
                    continue
                if any((
                        m[y + j][x + i] == 1
                        for i in [-1, 0, 1]
                        for j in [-1, 0, 1]
                        if 0 <= y + j < len(m) and 0 <= x + i < len(m[0])
                )):
                    cells.append(Cell(self.x + x, self.y + y, CellType.EMPTY_HIT))
        return cells

    def is_sunk(self, field: list[list[Cell]]) -> bool:
        for cell in self.get_occupied_cells():
            if field[cell.y][cell.x].type != CellType.SHIP_HIT:
                return False
        return True

    def overlap(self, other_ship: 'Ship') -> bool:
        ship_near_cells = self.get_surrounding_cells() + self.get_occupied_cells()
        other_ship_near_cells = other_ship.get_surrounding_cells() + other_ship.get_occupied_cells()
        for cell in ship_near_cells:
            if cell in other_ship_near_cells:
                return True

    def valid_position(self, board_size: tuple[int, int]) -> bool:  # (x, y)
        for cell in self.get_occupied_cells():
            if not (0 <= cell.x < board_size[0] and 0 <= cell.y < board_size[1]):
                return False
        return True
