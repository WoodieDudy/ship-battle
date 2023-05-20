from domain.ships.base_ship import Ship


class SmallShip(Ship):
    def get_matrix(self) -> list[list[int]]:
        return [
            [1, 0, 0],
            [0, 0, 0],
            [0, 0, 0],
        ]
