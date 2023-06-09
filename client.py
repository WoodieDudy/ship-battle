import threading
import traceback
import sys
import random
import logging
from typing import Optional

import pygame

from domain.board import Board
from helpers.classes import ResponseIterator
from domain.ships import *
from domain.player import Player
from proto_stuff.ShipBattle_pb2 import *
from proto_stuff.ShipBattle_pb2_grpc import *
from domain.games.client_game import ClientGame
from helpers.grpc_parser import *


logging.basicConfig(level=logging.INFO, filename="logs.txt", filemode="w",
                    format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

SERVER_URL = "localhost:50051"
COLORS = {
    CellType.EMPTY: (69, 145, 245),  # Голубой
    CellType.SHIP: (128, 84, 13),  # Коричневый
    CellType.SHIP_HIT: (200, 0, 0),  # Красный
    CellType.HIDDEN: (27, 12, 135),  # темно синий
    CellType.EMPTY_HIT: (220, 220, 220),  # Оранжевый
}

# Размеры
WINDOW_WIDTH, WINDOW_HEIGHT = 1200, 600
BOARD_PADDING = 50
BOARD_WIDTH, BOARD_HEIGHT = (WINDOW_WIDTH - 3 * BOARD_PADDING) // 2, WINDOW_HEIGHT - 2 * BOARD_PADDING
BOARD1_POS = (BOARD_PADDING, BOARD_PADDING)
BOARD2_POS = (BOARD_PADDING, 2 * BOARD_PADDING + BOARD_WIDTH)
BOARD_CELL_SIZE = 10
ships = [
    SmallShip,
    SubmarineShip,
    DiagonalShip,
    SquareShip,
]


class GameInterface:
    def __init__(self, game: ClientGame):
        self.game = game
        self.board_width, self.board_height = game.board_size, game.board_size
        self.cell_width, self.cell_height = BOARD_WIDTH // self.board_width, BOARD_HEIGHT // self.board_height
        self.current_status = "Waiting for the opponent..."

        pygame.init()
        pygame.font.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self._setup_game_interface()

    def _setup_game_interface(self):
        self.screen.fill((69, 145, 245))
        self._set_text('Your board', BOARD_PADDING + BOARD_WIDTH // 2, BOARD_PADDING // 2, 30)
        self._set_text('Enemy board', 2 * BOARD_PADDING + BOARD_WIDTH * 1.5, BOARD_PADDING // 2, 30)

    def _set_status_text(self):
        self._set_text(self.current_status, WINDOW_WIDTH // 2, WINDOW_HEIGHT - BOARD_PADDING // 2, 30)

    def draw_board(self, surface, game_board: Board, board_position):
        for y in range(self.board_height):
            for x in range(self.board_width):
                cell = game_board[y][x]
                color = COLORS[cell.type]
                if (cell.y, cell.x) in game_board.highlighted_cells:
                    color = tuple(map(lambda x: (x * 1.4) % 255, color))
                pygame.draw.rect(surface, color,
                                 pygame.Rect(board_position[0] + x * self.cell_width,
                                             board_position[1] + y * self.cell_height,
                                             self.cell_width, self.cell_height))
                pygame.draw.rect(surface, (255, 255, 255),
                                 pygame.Rect(board_position[0] + x * self.cell_width,
                                             board_position[1] + y * self.cell_height,
                                             self.cell_width, self.cell_height), 1)

    def highlight_cell(self, board, x, y):
        self.game.boards[0].highlighted_cells.clear()
        self.game.boards[1].highlighted_cells.clear()
        if board is not None:
            board.highlighted_cells.append((y, x))

    def render(self):
        self._setup_game_interface()
        self.draw_board(self.screen, self.game.boards[0], (BOARD_PADDING, BOARD_PADDING))
        self.draw_board(self.screen, self.game.boards[1], (2 * BOARD_PADDING + BOARD_WIDTH, BOARD_PADDING))
        self._set_status_text()
        pygame.display.flip()

    def get_cell_coords(self, mouse_x, mouse_y) -> Optional[tuple[Board, int, int]]:
        for board_pos, board in [(BOARD1_POS, self.game.boards[0]), (BOARD2_POS, self.game.boards[1])]:
            if board_pos[0] <= mouse_y < board_pos[0] + BOARD_WIDTH and \
                    board_pos[1] <= mouse_x < board_pos[1] + BOARD_HEIGHT:
                board_x = (mouse_x - board_pos[1]) // self.cell_width
                board_y = (mouse_y - board_pos[0]) // self.cell_height
                return board, board_x, board_y
        return None

    def _set_text(self, string, coordx, coordy, font_size):
        font = pygame.font.SysFont('arial', font_size)
        text = font.render(string, True, (0, 0, 0))
        textRect = text.get_rect()
        textRect.center = (coordx, coordy)
        self.screen.blit(text, textRect)

    def quit(self):
        logging.info("Quitting game")
        pygame.display.quit()
        pygame.quit()
        sys.exit()

    def events(self):
        for event in pygame.event.get():
            yield event


def _create_channel():
    channel = grpc.insecure_channel(SERVER_URL)
    try:
        grpc.channel_ready_future(channel).result(timeout=15)
        return channel
    except grpc.FutureTimeoutError as e:
        print("Cant connect to server")
        raise e


def main():
    ships_count = 6
    player_ships: list[Ship] = []
    for _ in range(ships_count):
        while True:
            ship = random.choice(ships)(random.randint(0, 10), random.randint(0, 10))
            if any(ship.overlap(other_ship) for other_ship in player_ships):
                continue
            if ship.valid_position((BOARD_CELL_SIZE, BOARD_CELL_SIZE)):
                break
        player_ships.append(ship)

    response_iterator = ResponseIterator()
    ship_battle_channel = _create_channel()
    ship_client = BattleshipServiceStub(ship_battle_channel)

    response_iterator.add_response(
        EventRequest(
            create_game_request=CreateGameRequest(
                ships=[
                    python_ship_to_proto_ship(ship)
                    for ship in player_ships
                ],
                wait_for_friend=False
            )
        ))

    for response in ship_client.listenEvents(response_iterator):
        logging.info(str(response))
        event = response.WhichOneof('event')
        if event == 'create_game_response':
            response = response.create_game_response
            if response.status == CreateGameStatus.Value("GAME_ID_DOENT_EXIST"):
                logging.info('Game id doesnt exist')
            elif response.status == CreateGameStatus.Value("ADDED_TO_Q"):
                game_id = response.game_id
                player_id = response.player_id
                logging.info(f"game id: {game_id}, player id: {player_id}")
                logging.info('Added to queue')

            elif response.status == CreateGameStatus.Value("GAME_STARTED_YOUR_TURN"):
                logging.info('Ready Your turn')
                first_game_status = 'Your turn'
                break
            elif response.status == CreateGameStatus.Value("GAME_STARTED_ENEMY_TURN"):
                logging.info('Ready Enemy turn')
                first_game_status = 'Enemy turn'
                break
            else:
                raise Exception("Unknown status")

    game = ClientGame(
        Player(id=player_id, ships=player_ships),
        board_size=BOARD_CELL_SIZE
    )
    game.id = game_id
    game_interface = GameInterface(game)
    game_interface.current_status = first_game_status
    game_interface.render()

    def interface_loop(request_iter: ResponseIterator):
        running = True
        while running:
            game_interface.render()
            for event in game_interface.events():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    res = game_interface.get_cell_coords(*pygame.mouse.get_pos())
                    if res is None:
                        continue
                    b, x, y = res
                    if b == game.boards[0] or not game.running:
                        continue
                    print(f"Clicked on {x} {y}")
                    if b[y][x].type == CellType.HIDDEN:
                        request_iter.add_response(
                            EventRequest(move_request=MoveRequest(
                                point=Point(x=x, y=y),
                                game_id=game.id,
                                player_id=game.player_id),
                            )
                        )
                        print(f"Sent")
                    else:
                        print(f"Already clicked")
                elif event.type == pygame.QUIT:
                    running = False
                    # request_iter.add_response(
                    #     EventRequest(quit_request=QuitRequest(
                    #         game_id=game.id,
                    #         player_id=game.player_id
                    #     ))
                    # )
                    logging.info("Quit")
                    game_interface.quit()
                else:
                    res = game_interface.get_cell_coords(*pygame.mouse.get_pos())
                    if res is None:
                        continue
                    b, x, y = res
                    game_interface.highlight_cell(b, x, y)

        pygame.quit()
        return

    def process_requests_loop(request_iterator: ResponseIterator):
        for response in ship_client.listenEvents(request_iterator):
            logging.info(str(response))
            event = response.WhichOneof('event')
            if event == 'create_game_response':
                response = response.create_game_response
                if response.status == CreateGameStatus.Value("GAME_ID_DOENT_EXIST"):
                    logging.info('Game id doesnt exist')
                elif response.status == CreateGameStatus.Value("ADDED_TO_Q"):
                    game.id = response.game_id
                    game.player_id = response.player_id
                    logging.info(f"game id: {game.id}, player id: {game.player_id}")
                    logging.info('Added to queue')
                    listen_enemy_moves_thread = threading.Thread(target=listen_enemy_moves, args=(ship_client, game))
                    listen_enemy_moves_thread.start()

            elif event == 'move_response':
                response = response.move_response
                if response.status == MoveStatus.Value("NOT_YOUR_TURN"):
                    logging.info('Not your turn')
                elif response.status == MoveStatus.Value("GAME_NOT_STARTED"):
                    logging.info('Game not started')
                elif response.status == MoveStatus.Value("INVALID_COORDINATES"):
                    logging.info('Invalid coordinates')
                elif response.status == MoveStatus.Value("TURN"):
                    cells = [
                        proto_cell_to_python_cell(cell)
                        for cell in response.revealed_cells
                    ]
                    game.reveal_enemy_hit_cells(cells)
                    if all((cell.type != CellType.SHIP_HIT for cell in cells)):
                        game_interface.current_status = "Enemy turn"
                elif response.status == MoveStatus.Value("WIN"):
                    cells = [
                        proto_cell_to_python_cell(cell)
                        for cell in response.revealed_cells
                    ]
                    game.reveal_enemy_hit_cells(cells)
                    game_interface.current_status = "You win"
                    game.running = False
            else:
                logging.info(f"Unknown status {response}")
                raise Exception(f"Unknown status {response}")

    def listen_enemy_moves(ship_client, game):
        logging.info("Amogus")
        enemy_moves_request = EnemyMovesRequest(
            game_id=game.id,
            player_id=game.player_id
        )
        for response in ship_client.listenEnemyMoves(enemy_moves_request):
            if response.status == EnemyMoveStatus.Value("ENEMY_LEAVE"):
                game_interface.current_status = "You win (enemy left)"
                logging.info('Enemy leave2')
            elif response.status == EnemyMoveStatus.Value("ENEMY_WIN"):
                revealed_cells = game.make_enemy_turn(response.point.x, response.point.y)
                game.reveal_my_cells(revealed_cells)
                logging.info('Enemy win')
                game_interface.current_status = "You lost"
                game.running = False
            elif response.status == EnemyMoveStatus.Value("ENEMY_TURN"):
                revealed_cells = game.make_enemy_turn(response.point.x, response.point.y)
                game.reveal_my_cells(revealed_cells)
                logging.info('Enemy turn2')
                if all((cell.type != CellType.SHIP_HIT for cell in revealed_cells)):
                    game_interface.current_status = "Your turn"
            else:
                logging.info(f"Unknown status {response}")
                raise Exception(f"Unknown status {response}")

    process_requests_thread = threading.Thread(target=process_requests_loop, args=(response_iterator,))
    process_requests_thread.start()
    listen_enemy_moves_thread = threading.Thread(target=listen_enemy_moves, args=(ship_client, game))
    listen_enemy_moves_thread.start()

    try:
        interface_loop(response_iterator)
    finally:
        logging.info(traceback.format_exc())
        process_requests_thread.join()
        listen_enemy_moves_thread.join()


if __name__ == "__main__":
    main()
