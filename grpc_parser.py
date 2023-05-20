from core import Cell, CellType
from proto_stuff import ShipBattle_pb2
from domain.ships import *


def proto_ship_to_python_ship(proto_ship: ShipBattle_pb2.Ship) -> Ship:
    ship_type = proto_ship.ship_type
    if ship_type == ShipBattle_pb2.ShipType.Value("SMALL"):
        return SmallShip(proto_ship.x, proto_ship.y)
    elif ship_type == ShipBattle_pb2.ShipType.Value("SUBMARINE"):
        return SubmarineShip(proto_ship.x, proto_ship.y)
    elif ship_type == ShipBattle_pb2.ShipType.Value("DIAGONAL"):
        return DiagonalShip(proto_ship.x, proto_ship.y)
    elif ship_type == ShipBattle_pb2.ShipType.Value("SQUARE"):
        return SquareShip(proto_ship.x, proto_ship.y)
    else:
        raise Exception("Unknown ship type")


def python_ship_to_proto_ship(python_ship: Ship) -> ShipBattle_pb2.Ship:
    proto_ship = ShipBattle_pb2.Ship()
    proto_ship.x = python_ship.x
    proto_ship.y = python_ship.y
    if isinstance(python_ship, SmallShip):
        proto_ship.ship_type = ShipBattle_pb2.ShipType.Value("SMALL")
    elif isinstance(python_ship, SubmarineShip):
        proto_ship.ship_type = ShipBattle_pb2.ShipType.Value("SUBMARINE")
    elif isinstance(python_ship, DiagonalShip):
        proto_ship.ship_type = ShipBattle_pb2.ShipType.Value("DIAGONAL")
    elif isinstance(python_ship, SquareShip):
        proto_ship.ship_type = ShipBattle_pb2.ShipType.Value("SQUARE")
    else:
        raise Exception("Unknown ship type")
    return proto_ship


def proto_cell_to_python_cell(proto_cell: ShipBattle_pb2.Cell) -> Cell:
    return Cell(proto_cell.point.x, proto_cell.point.y, CellType(proto_cell.type))


def python_cell_to_proto_cell(python_cell: Cell) -> ShipBattle_pb2.Cell:
    proto_cell = ShipBattle_pb2.Cell(
        point=ShipBattle_pb2.Point(x=python_cell.x, y=python_cell.y),
        type=ShipBattle_pb2.CellType.Name(int(python_cell.type))
    )
    return proto_cell
