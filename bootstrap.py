import logging

from entry_points.base_entry_point import EntryPoint
from entry_points.entry_point_runner import EntryPointRunner
from helpers.log import Logger


class AppStarter:
    def __init__(self, logger: Logger, entry_point_runner: EntryPointRunner, entry_points: list[EntryPoint]):
        self._logger = logger
        self._entry_point_runner = entry_point_runner
        self._entry_points = entry_points

    def start(self):
        bone_logger = self._logger.logger
        bone_logger.setLevel(logging.DEBUG)

        for entry_point in self._entry_points:
            self._entry_point_runner.run(entry_point)

    def wait_to_finish(self):
        self._entry_point_runner.wait_for_all()
