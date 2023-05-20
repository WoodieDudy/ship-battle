from domain.ships.base_ship import Ship


class SubmarineShip(Ship):
    def get_matrix(self) -> list[list[int]]:
        return [
            [1, 1, 1],
            [0, 0, 0],
            [0, 0, 0],
        ]
