import logging

from fastapi import HTTPException

from src.core.model.circuit import Circuit
from src.infrastructure.repositories.circuit_breaker_repository import (
    CircuitBreakerRepository,
)


class CircuitBreakerService:
    logger = logging.getLogger(__name__)

    def __init__(self, repository: CircuitBreakerRepository):
        self._repository: CircuitBreakerRepository = repository

    def add_circuit(self, circuit: Circuit):
        self._repository.add(circuit)

    def get_circuit(self, circuit_id: str) -> Circuit:
        return self._repository.get(circuit_id)

    async def execute(self, circuit_id, function, fallback_function):
        circuit = self._repository.get(circuit_id)

        if circuit is None:
            raise HTTPException(status_code=500, detail="Circuit does not exist")

        if circuit.is_callable():
            try:
                self.logger.info(f"Calling function for: {circuit}")
                response = await function()
                self.logger.info(f"Function call succeeded for circuit '{circuit_id}'")
                circuit.handle_successful_call()
                self._repository.update(circuit)
                return response
            except Exception as e:
                self.logger.info(
                    f"Function call failed for circuit '{circuit_id}', falling back: {e}"
                )
                circuit.handle_failed_call()
                self._repository.update(circuit)
                return await fallback_function()
        else:
            self.logger.info(f"Circuit '{circuit_id}' is tripped, calling fallback")
            return await fallback_function()
