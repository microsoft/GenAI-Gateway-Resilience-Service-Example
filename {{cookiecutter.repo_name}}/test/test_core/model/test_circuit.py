from time import time
from unittest import TestCase
from src.core.model.circuit import Circuit
from unittest.mock import patch


class Test(TestCase):
    def test_trip_opens_circuit(self):
        circuit = Circuit(
            identifier="test",
            failure_threshold=3,
            retry_timeout=1000,
            last_failure=None,
            open=False,
            failure_count=0,
        )

        circuit.trip()
        assert circuit.open

    def test_handle_failed_call_trips_circuit(self):
        circuit = Circuit(
            identifier="test",
            failure_threshold=3,
            retry_timeout=1000,
            last_failure=None,
            open=False,
            failure_count=0,
        )

        assert circuit.is_callable()
        circuit.handle_failed_call()
        assert circuit.is_callable()
        circuit.handle_failed_call()
        assert circuit.is_callable()
        circuit.handle_failed_call()
        assert not circuit.is_callable()

    def test_circuit_is_callable_after_retry_timeout(self):
        circuit = Circuit(
            identifier="test",
            failure_threshold=3,
            retry_timeout=3,
            last_failure=None,
            open=False,
            failure_count=0,
        )

        assert circuit.is_callable()
        circuit.handle_failed_call()
        circuit.handle_failed_call()
        circuit.handle_failed_call()
        assert not circuit.is_callable()

        current_time = time()

        with patch("src.core.model.circuit.time") as time_mock:
            # Simulate a delay of 1 second. The circuit is still open.
            time_mock.return_value = current_time + 1
            assert not circuit.is_callable()

            # Simulate a delay of another 2 seconds. The circuit is now closed.
            time_mock.return_value += 2
            assert circuit.is_callable()

    def test_circuitresets_resets_after_successful_call(self):
        circuit = Circuit(
            identifier="test",
            failure_threshold=3,
            retry_timeout=4,
            last_failure=None,
            open=True,
            failure_count=5,
        )

        circuit.handle_successful_call()
        assert circuit.failure_count == 0
        assert not circuit.open
        assert circuit.last_failure is None

    def test_reset_circuit(self):
        circuit = Circuit(
            identifier="test",
            failure_threshold=3,
            retry_timeout=4,
            last_failure=time(),
            open=True,
            failure_count=5,
        )

        circuit.reset_circuit()
        assert not circuit.open
        assert circuit.last_failure is None
        assert circuit.failure_count == 0

    def test_is_retry_time(self):
        circuit = Circuit(
            identifier="test",
            failure_threshold=3,
            retry_timeout=100,
            last_failure=None,
            open=True,
            failure_count=5,
        )

        assert not circuit.is_retry_time()
        circuit.last_failure = time() - 1000
        assert circuit.is_retry_time()
        circuit.last_failure = time() - 10
        assert not circuit.is_retry_time()
