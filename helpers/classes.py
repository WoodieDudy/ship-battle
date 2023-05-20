import queue


class ResponseIterator:
    def __init__(self):
        self._queue = queue.SimpleQueue()

    def __iter__(self):
        return self

    def __next__(self):
        return self._queue.get()

    def add_response(self, response):
        self._queue.put(response)
