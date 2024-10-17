import heapq
import numpy as np


class PriorityQueue:
    def __init__(self):
        self._queue = []
        self.item_count = 0

    def push(self, item, priority):
        heapq.heappush(self._queue, (priority, self.item_count, item))
        self.item_count += 1

    def empty(self):
        return not self._queue

    def pop(self):
        _, _, item = heapq.heappop(self._queue)
        return item


def harmonic_mean(arr):
    m = 0
    for i in arr:
        m += 1.0 / i
    return len(arr) / m
    
def geometric_mean(arr):
    a = np.log(arr)
    return np.exp(a.mean())
