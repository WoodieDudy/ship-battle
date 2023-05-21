from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Singleton, List

from bootstrap import AppStarter
from entry_points.entry_point_runner import EntryPointRunner
from entry_points.grpc_entry_point import GrpcEntryPoint
from helpers.log import Logger
from services.game_server import Server


class Container(DeclarativeContainer):
    logger = Singleton(Logger)
    game_server = Singleton(Server, logger=logger)

    grpc_entry_point = Singleton(
        GrpcEntryPoint,
        logger=logger,
        server=game_server,
    )

    entry_point_runner = Singleton(
        EntryPointRunner,
        logger=logger,
    )

    app_starter = Singleton(
        AppStarter,
        logger=logger,
        entry_point_runner=entry_point_runner,
        entry_points=List(
            grpc_entry_point,
        ),
    )
