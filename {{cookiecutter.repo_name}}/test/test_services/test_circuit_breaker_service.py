from fastapi import HTTPException

from src.infrastructure.repositories.in_memory_circuit_breaker_repository import (
    InMemoryCircuitBreakerRepository,
)
from src.services.circuit_breaker_service import CircuitBreakerService
from src.core.model.circuit import Circuit
from unittest import TestCase
import asyncio


class Test(TestCase):
    def setUp(self):
        self.repository = InMemoryCircuitBreakerRepository()
        self.service = CircuitBreakerService(self.repository)

    def test_add_circuit(self):
        expected_circuit = Circuit(
            identifier="primary", failure_threshold=1, retry_timeout=1
        )
        self.service.add_circuit(expected_circuit)
        self.assertTrue(
            self.repository.get(expected_circuit.identifier) == expected_circuit
        )

    def test_get_circuit(self):
        expected_circuit = Circuit(
            identifier="primary", failure_threshold=1, retry_timeout=1
        )
        self.repository.add(expected_circuit)
        actual_circuit = self.service.get_circuit(expected_circuit.identifier)
        self.assertTrue(actual_circuit == expected_circuit)

    def test_execute_calls_function(self):
        function_calls = 0
        fallback_function_calls = 0
        loop = asyncio.get_event_loop()

        async def test_function():
            nonlocal function_calls
            function_calls += 1
            return "function called"

        async def test_fallback_function():
            nonlocal fallback_function_calls
            fallback_function_calls += 1
            return "fallback function called"

        self.service.add_circuit(Circuit("test-circuit"))
        response = loop.run_until_complete(
            self.service.execute(
                "test-circuit",
                lambda: test_function(),
                lambda: test_fallback_function(),
            )
        )

        self.assertTrue(function_calls == 1)
        self.assertTrue(fallback_function_calls == 0)
        self.assertTrue(response == "function called")

    def test_execute_calls_fallback_function_if_function_fails(self):
        function_calls = 0
        fallback_function_calls = 0
        loop = asyncio.get_event_loop()

        async def test_function():
            nonlocal function_calls
            function_calls += 1
            raise Exception("Failure")

        async def test_fallback_function():
            nonlocal fallback_function_calls
            fallback_function_calls += 1
            return "fallback function called"

        self.service.add_circuit(Circuit("test-circuit"))
        response = loop.run_until_complete(
            self.service.execute(
                "test-circuit",
                lambda: test_function(),
                lambda: test_fallback_function(),
            )
        )

        self.assertTrue(function_calls == 1)
        self.assertTrue(fallback_function_calls == 1)
        self.assertTrue(response == "fallback function called")

    def test_execute_propagates_fallback_function_exception(self):
        loop = asyncio.get_event_loop()
        self.service.add_circuit(Circuit("test-circuit"))

        async def test_function():
            raise Exception("Failure")

        expected_exception = Exception("Fallback Failure")

        async def test_fallback_function():
            nonlocal expected_exception
            raise expected_exception

        with self.assertRaises(Exception) as exception_context:
            loop.run_until_complete(
                self.service.execute(
                    "test-circuit",
                    lambda: test_function(),
                    lambda: test_fallback_function(),
                )
            )

        self.assertTrue(exception_context.exception == expected_exception)

    def test_execute_calls_fallback_function_if_circuit_tripped(self):
        function_calls = 0
        fallback_function_calls = 0

        loop = asyncio.get_event_loop()
        self.service.add_circuit(Circuit("test-circuit", open=True))

        async def test_function():
            raise Exception("Failure")

        async def test_fallback_function():
            nonlocal fallback_function_calls
            fallback_function_calls += 1
            return "fallback function called"

        response = loop.run_until_complete(
            self.service.execute(
                "test-circuit",
                lambda: test_function(),
                lambda: test_fallback_function(),
            )
        )

        self.assertTrue(function_calls == 0)
        self.assertTrue(fallback_function_calls == 1)
        self.assertTrue(response == "fallback function called")

    def test_execute_handles_failed_call(self):
        function_calls = 0
        fallback_function_calls = 0
        loop = asyncio.get_event_loop()

        async def test_function():
            raise Exception()

        async def test_fallback_function():
            nonlocal fallback_function_calls
            fallback_function_calls += 1
            return "fallback function called"

        circuit = Circuit("test-circuit")
        self.service.add_circuit(circuit)
        response = loop.run_until_complete(
            self.service.execute(
                "test-circuit",
                lambda: test_function(),
                lambda: test_fallback_function(),
            )
        )

        self.assertTrue(function_calls == 0)
        self.assertTrue(fallback_function_calls == 1)
        self.assertTrue(response == "fallback function called")
        self.assertTrue(circuit.failure_count == 1)

    def test_execute_throws_exception_for_non_existing_circuit(self):
        loop = asyncio.get_event_loop()

        async def test_function():
            return "primary function called"

        async def test_fallback_function():
            return "fallback function called"

        with self.assertRaises(HTTPException) as context:
            loop.run_until_complete(
                self.service.execute(
                    "test-circuit",
                    lambda: test_function(),
                    lambda: test_fallback_function(),
                )
            )

        self.assertEqual("Circuit does not exist", context.exception.detail)
        self.assertEqual(500, context.exception.status_code)
