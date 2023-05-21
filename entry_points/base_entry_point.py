import abc


class EntryPoint(abc.ABC):
    @abc.abstractmethod
    def run(self) -> None: ...

    @abc.abstractmethod
    def get_name(self) -> str: ...
