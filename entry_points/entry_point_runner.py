from threading import Thread

from entry_points.base_entry_point import EntryPoint
from helpers.log import Logger


class EntryPointRunner:
    def __init__(self, logger: Logger):
        self._logger = logger
        self._threads = []

    def run(self, entry_point: EntryPoint):
        def _run():
            try:
                name = entry_point.get_name()
                self._logger.info(f"Starting {name}")
                entry_point.run()
                self._logger.info(f"Finished {name}")
            except Exception as e:
                self._logger.error(f'Unexpected error while running "{entry_point.get_name()}": {repr(e)}')
                self._logger.exception(e)

        thread = Thread(target=_run)
        thread.start()
        self._threads.append(thread)

    def wait_for_all(self):
        for thread in self._threads:
            thread.join()
