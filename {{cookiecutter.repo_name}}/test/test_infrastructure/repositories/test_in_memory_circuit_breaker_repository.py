from unittest import TestCase
from src.infrastructure.repositories.in_memory_circuit_breaker_repository \
    import InMemoryCircuitBreakerRepository
from src.core.model.circuit import Circuit


class Test(TestCase):

    def setUp(self):
        self.repository = InMemoryCircuitBreakerRepository()

    def test_adding_and_getting_circuit(self):
        circuit = Circuit("some-identifier")
        self.repository.add(circuit)
        self.assertTrue(self.repository.get(circuit.identifier) == circuit)

    def test_updating_circuit(self):
        circuit = Circuit("some-identifier", failure_threshold=5)
        self.repository.add(circuit)
        self.assertTrue(
            self.repository.get(circuit.identifier).failure_threshold == 5
        )
        circuit.failure_threshold = 10
        self.assertTrue(
            self.repository.get(circuit.identifier).failure_threshold == 10
            )

    def test_update_noop(self):
        circuit = Circuit("some-identifier", failure_threshold=5)
        self.repository.update(circuit)

    def test_get_returns_none_if_not_exists(self):
        self.assertTrue(self.repository.get("does not exist") is None)
