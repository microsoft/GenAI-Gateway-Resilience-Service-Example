from dependency_injector import containers, providers
from src.settings import Settings
from src.services.circuit_breaker_service import CircuitBreakerService
from src.infrastructure.repositories.in_memory_circuit_breaker_repository import (
    InMemoryCircuitBreakerRepository
)


def setup_dependency_container(app, modules=None, packages=None):
    container = DependencyContainer()
    app.container = container
    app.container.wire(modules=modules, packages=packages)
    return app


class DependencyContainer(containers.DeclarativeContainer):
    config = providers.Configuration()
    wiring_config = containers.WiringConfiguration()
    settings = providers.ThreadSafeSingleton(
        Settings
    )
    circuit_breaker_repository = providers.ThreadSafeSingleton(
        InMemoryCircuitBreakerRepository
    )
    circuit_breaker_service = providers.Factory(
        CircuitBreakerService,
        repository=circuit_breaker_repository
    )
