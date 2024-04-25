import logging
from time import time


class Circuit:
    """
    Circuit class to keep track of a circuit to a specific resource.

    It has the following attributes:
        - id: unique id for the circuit
        - failure_threshold: maximum concurrent failures until the circuit opens
        - retry_timeout: time in seconds until the circuit is open again.
        - last_failure: time the last failure was recorded.
        - open: flag set to true if circuit is open.
        - failure_count: number of concurrent failures recorded in the circuit.
    """

    logger = logging.getLogger(__name__)

    def __init__(
        self,
        identifier,
        failure_threshold=3,
        retry_timeout=10,
        last_failure=None,
        failure_count=0,
        open=False,
    ):
        self.identifier = identifier
        self.failure_threshold = failure_threshold
        self.retry_timeout = retry_timeout
        self.last_failure = last_failure
        self.open = open
        self.failure_count = failure_count

    def reset_circuit(self):
        self.logger.info(f"Resetting circuit: {self.identifier}")
        self.open = False
        self.last_failure = None
        self.failure_count = 0

    def is_retry_time(self):
        if self.last_failure is None:
            return False

        return time() - self.last_failure >= self.retry_timeout

    def trip(self):
        self.logger.info(f"Tripping circuit: {self.identifier}")
        self.open = True

    def handle_successful_call(self):
        self.reset_circuit()

    def handle_failed_call(self):
        self.failure_count += 1
        self.last_failure = time()

        if self.failure_count >= self.failure_threshold:
            self.trip()

    def is_callable(self):
        if self.is_retry_time():
            return True

        if self.open:
            return False

        return True

    def __str__(self):
        return (
            f"['identifier': '{self.identifier}', 'failure_threshold': '{self.failure_threshold}', "
            f"'retry_timeout': '{self.retry_timeout}', 'last_failure': '{self.last_failure}', "
            f"'open': '{self.open}', 'failure_count': '{self.failure_count}']"
        )
