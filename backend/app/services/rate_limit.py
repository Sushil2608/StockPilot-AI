from collections import deque
from math import ceil
from threading import Lock
from time import monotonic


class RateLimitExceeded(Exception):
    def __init__(self, retry_after: int) -> None:
        self.retry_after = retry_after
        super().__init__("Analysis rate limit exceeded")


class InMemoryRateLimiter:
    """Small per-process sliding-window limiter for expensive analysis requests."""

    def __init__(self, limit: int, window_seconds: int) -> None:
        self.limit = limit
        self.window_seconds = window_seconds
        self._requests: dict[str, deque[float]] = {}
        self._lock = Lock()

    def check(self, key: str) -> None:
        now = monotonic()
        cutoff = now - self.window_seconds

        with self._lock:
            for client, timestamps in list(self._requests.items()):
                while timestamps and timestamps[0] <= cutoff:
                    timestamps.popleft()
                if not timestamps:
                    del self._requests[client]

            timestamps = self._requests.setdefault(key, deque())
            if len(timestamps) >= self.limit:
                retry_after = ceil(self.window_seconds - (now - timestamps[0]))
                raise RateLimitExceeded(max(1, retry_after))

            timestamps.append(now)
