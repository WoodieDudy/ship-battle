import queue
import threading


class ResponseIterator:
    def __init__(self):
        self._queue = queue.SimpleQueue()

    def __iter__(self):
        return self

    def __next__(self):
        return self._queue.get()

    def add_response(self, response):
        self._queue.put(response)


class ThreadsRunner:
    def __init__(self):
        self._threads = []

    def spawn_thread(self, target, *args, **kwargs):
        thread = threading.Thread(target=target, args=args, kwargs=kwargs)
        thread.start()
        self._threads.append(thread)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.join_all()

    def join_all(self):
        for thread in self._threads:
            thread.join()

        self._threads.clear()
