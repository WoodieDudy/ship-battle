from concurrent import futures
from time import sleep
import traceback

import grpc

from grpc_parser import *
from player import Player
from proto_stuff.ShipBattle_pb2 import *
from proto_stuff import ShipBattle_pb2_grpc
from server import Server
from classes import *


class BattleshipServiceServicer(ShipBattle_pb2_grpc.BattleshipServiceServicer):
    def __init__(self):
        super().__init__()
        self.server = Server(self)
        self.enemy_moves: dict[str, list[EnemyMoveResponse]] = {}

    def listenEvents(self, request_iterator, context):
        for request in request_iterator:
            print(request)
            event = request.WhichOneof('event')
            if event == 'create_game_request':
                request = request.create_game_request
                player = Player(
                    ships=[
                        proto_ship_to_python_ship(ship)
                        for ship in request.ships
                    ],
                )
                game_id = request.game_id
                player_id, game_id = self.server.create_game(player, request.wait_for_friend, game_id)
                if player_id == 'no_game_id':
                    yield EventResponse(
                        create_game_response=CreateGameResponse(
                            status=ShipBattle_pb2.CreateGameStatus.Value("GAME_ID_DOENT_EXIST")))
                else:
                    yield EventResponse(
                        create_game_response=CreateGameResponse(
                            game_id=game_id,
                            player_id=player_id,
                            status=ShipBattle_pb2.CreateGameStatus.Value("ADDED_TO_Q")))
                while True:
                    game = self.server.get_game_by_id(game_id)
                    if game is not None:
                        break
                    sleep(1)

                yield EventResponse(
                    create_game_response=ShipBattle_pb2.CreateGameResponse(
                        game_id=game_id,
                        player_id=player_id,
                        status=ShipBattle_pb2.CreateGameStatus.Value("READY")
                    )
                )

            elif event == 'move_request':
                request = request.move_request
                yield EventResponse(
                    move_response=self.server.make_move(request.game_id, request.player_id, request.point.x, request.point.y)
                )

            elif event == 'quit_request':
                request = request.quit_request
                key = f'{request.game_id}{request.player_id}'
                self.enemy_moves[key].append(EnemyMoveResponse(status=ShipBattle_pb2.EnemyMoveStatus.Value('ENEMY_LEAVE')))
            else:
                raise Exception(f"Unknown event: {event}")

    def listenEnemyMoves(self, request, context) -> EnemyMoveResponse:
        key = f'{request.game_id}{request.player_id}'
        while True:
            while not self.enemy_moves.get(key):
                sleep(1)
            enemy_move = self.enemy_moves[key].pop(0)
            print(enemy_move)
            yield EnemyMoveResponse(
                status=enemy_move.status,
                point=enemy_move.point
            )

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    ShipBattle_pb2_grpc.add_BattleshipServiceServicer_to_server(BattleshipServiceServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("Server started")
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
