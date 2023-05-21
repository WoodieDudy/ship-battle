from domain.cell import CellType, Cell
from domain.ships.base_ship import Ship


class Board:
    def __init__(self, ships: list[Ship],
                 default_cell_type: CellType = CellType.EMPTY, size: int = 10):
        self.size = size
        self.ships = ships
        self.field = self._create_field(ships, default_cell_type)
        self.highlighted_cells = []

    def get_ship_by_coords(self, x, y) -> Ship | None:
        for ship in self.ships:
            if ship.point_inside(x, y):
                return ship
        return None

    def _create_field(self, ships: list[Ship], default: CellType) -> list[list[Cell]]:
        field = [[Cell(x, y, default) for x in range(self.size)] for y in range(self.size)]
        for ship in ships:
            for y, row in enumerate(ship.get_matrix()):
                for x, cell in enumerate(row):
                    if cell == 1:
                        field[ship.y + y][ship.x + x].type = CellType.SHIP
        return field

    def all_ships_sunk(self) -> bool:
        for row in self.field:
            for cell in row:
                if cell.type == CellType.SHIP:
                    return False
        return True

    def get_cells_of_sunken_ship(self, x, y) -> list[Cell]:
        ship = self.get_ship_by_coords(x, y)
        if ship is None:
            return []
        cells = ship.get_occupied_cells()
        cells += ship.get_surrounding_cells()
        return self._filter_outside_cells(cells)

    def _filter_outside_cells(self, cells: list[Cell]) -> list[Cell]:
        return [cell for cell in cells if 0 <= cell.x < self.size and 0 <= cell.y < self.size]

    def size(self):
        return len(self.field), len(self.field[0])

    def __getitem__(self, item):
        return self.field[item]

    def __len__(self):
        return len(self.field)

