from threading import Timer
from time import monotonic_ns
from typing import Callable


class CountdownTimer:
    def __init__(self, time_ms: int, callback: Callable):
        self._delay_ms = time_ms
        self._callback = callback
        self._timer = None
        self._start_time_ms = None

    def _run(self):
        self._callback()
        self._timer = None
        self._start_time_ms = None

    def start(self) -> None:
        if self._delay_ms <= 0:
            raise ValueError("Delay must be greater than 0 to start the countdown")
        if not callable(self._callback):
            raise ValueError("Delay must be a function")
        if self._timer is not None:
            return

        self._start_time_ms = monotonic_ns() / 1_000_000
        interval_s = self._delay_ms / 1000
        self._timer = Timer(interval_s, self._run)
        self._timer.start()

    def stop(self) -> None:
        if self._timer is None:
            return

        self._timer.cancel()
        self._timer = None
        self._start_time_ms = None

    def get_remaining_time(self) -> int | None:
        if self._timer is None:
            return None

        now_ms = monotonic_ns() / 1_000_000
        elapsed_time_ms = now_ms - self._start_time_ms
        remaining_time_ms = self._delay_ms - elapsed_time_ms
        return max(0, remaining_time_ms)

    def get_total_time(self) -> int:
        return self._delay_ms
