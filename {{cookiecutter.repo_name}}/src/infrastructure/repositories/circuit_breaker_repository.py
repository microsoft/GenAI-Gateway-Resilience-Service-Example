from abc import ABC, abstractmethod
from src.core.model.circuit import Circuit


class CircuitBreakerRepository(ABC):
    @abstractmethod
    def add(self, circuit: Circuit):
        raise NotImplementedError()

    @abstractmethod
    def update(self, circuit: Circuit):
        raise NotImplementedError()

    @abstractmethod
    def get(self, circuit_id: str):
        raise NotImplementedError()
