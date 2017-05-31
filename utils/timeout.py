"""
Context manager for running an operation with a timeout. Only works on Unix systems.
"""

import signal


class TimeoutException(Exception):
    pass


class Timeout:

    def __init__(self, timeout):
        self.timeout = timeout

    def __enter__(self):
        def raise_timeout(*_):
            raise TimeoutException()

        signal.signal(signal.SIGALRM, raise_timeout)
        signal.alarm(self.timeout)

    def __exit__(self, exc_type, exc_val, exc_tb):
        signal.alarm(0)
