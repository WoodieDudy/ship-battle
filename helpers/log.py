import contextlib
import logging
import math
import os
import sys
import time
import warnings

import colorama
import colorlog


class Logger:
    __instance__ = None
    __logger = None

    def __new__(cls, *args, **kwargs):
        if not cls.__instance__:
            cls.__instance__ = super().__new__(cls, *args, **kwargs)
        return cls.__instance__

    def __init__(self, indent: str = "-- "):
        if self.__logger:
            return

        self._indent_level = 0
        self._indent = indent
        self._averages: dict[int, list[int]] = dict()

        # Create clean logger
        self.__logger = logging.RootLogger(logging.NOTSET)

        handler = colorlog.StreamHandler()
        formatter = colorlog.ColoredFormatter('%(log_color)s[%(levelname)s] [%(asctime)s]    %(message)s')
        handler.setFormatter(formatter)

        self.__logger.addHandler(handler)
        self.__logger.setLevel(logging.DEBUG)

    def _apply_indent(self, message) -> str:
        return self._indent_level * self._indent + str(message)

    def debug(self, message):
        self.__logger.debug(self._apply_indent(message))

    def info(self, message):
        self.__logger.info(self._apply_indent(message))

    def error(self, error):
        self.__logger.error(self._apply_indent(error))

    def exception(self, exception):
        self.__logger.exception(exception)

    def warn(self, warning):
        self.__logger.warning(self._apply_indent(warning))

    @property
    def logger(self):
        return self.__logger

    def increase_indent(self):
        self._indent_level += 1

    def decrease_indent(self):
        self._indent_level = max(0, self._indent_level - 1)

    @contextlib.contextmanager
    def indent(self):
        self.increase_indent()

        try:
            yield
        finally:
            self.decrease_indent()

    @contextlib.contextmanager
    def ignore_indent(self, indent_level: int = 0):
        assert indent_level >= 0

        indent = self._indent_level
        self._indent_level = indent_level
        try:
            yield
        finally:
            self._indent_level = indent

    @contextlib.contextmanager
    def begin_scope(self, section_name: str, /, contrib_average: bool = False, supress_exceptions: bool = False):
        name_colors = [colorama.Fore.BLUE, colorama.Fore.YELLOW, colorama.Fore.MAGENTA, colorama.Fore.LIGHTRED_EX]

        indent = self._indent_level
        name_color = name_colors[indent % len(name_colors)]

        green = colorama.Fore.LIGHTGREEN_EX
        red = colorama.Fore.RED
        reset = colorama.Fore.RESET

        self.debug(f"{name_color}{section_name}{reset} started:")
        start_t = time.perf_counter()

        try:
            with self.indent():
                yield
        except Exception as e:
            self.exception(e)
            if not supress_exceptions:
                raise e
        else:
            end_t = time.perf_counter()
            passed_t = end_t - start_t
            passed_t_ms = math.ceil(passed_t * 1000)

            if contrib_average:
                self._averages[indent] = self._averages.get(indent + 1, [0, 0])
                self._averages[indent][0] += passed_t_ms
                self._averages[indent][1] += 1

            passed_time_str = f" Passed time: {green}{passed_t_ms:,}ms{reset}."
            if indent + 1 in self._averages:
                total, count = self._averages.pop(indent + 1)
                passed_time_str += f" Average time: {green}{round(total / count):,}ms{reset}." \
                                   f" Total calls: {green}{count:,}{reset}."

            self.debug(f"{name_color}{section_name}{reset} {green}done{reset}.{passed_time_str}\n")


@contextlib.contextmanager
def devnull():
    original_stdout = sys.stdout
    sys.stdout = open(os.devnull, 'w')
    try:
        yield
    finally:
        sys.stdout.close()
        sys.stdout = original_stdout


def get_logger() -> Logger:
    warnings.warn("get_logger() is deprecated, use Logger() instead.", DeprecationWarning)
    return Logger.__instance__ or Logger()
