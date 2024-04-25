from src.infrastructure.repositories.circuit_breaker_repository import (
    CircuitBreakerRepository,
)
from src.core.model.circuit import Circuit


class InMemoryCircuitBreakerRepository(CircuitBreakerRepository):
    def __init__(self):
        self.store = {}

    def add(self, circuit: Circuit):
        self.store[circuit.identifier] = circuit

    def update(self, circuit: Circuit):
        """
        Explicit updates are not required for an in memory repository. Updates to the circuit object are automatically
        updated in the store.
        """

    def get(self, circuit_id: str):
        if circuit_id in self.store:
            return self.store[circuit_id]
        else:
            return None
