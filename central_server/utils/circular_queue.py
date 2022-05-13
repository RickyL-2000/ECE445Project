import queue


class CircularQueue(queue.Queue):
    def __init__(self, maxsize):
        super().__init__(maxsize)

    def put(self, *arg, **kwarg):
        if self.full():
            self.get(block=False)
        super().put(*arg, **kwarg)
