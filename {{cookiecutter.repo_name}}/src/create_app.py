import logging
import os

from azure.monitor.opentelemetry import configure_azure_monitor
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from src.dependency_container import setup_dependency_container
from src.api.routers import router as api_router
from src.core.model.circuit import Circuit
from src.services import CircuitBreakerService
from src.settings import Settings

logger = logging.getLogger(__name__)


async def catch_all_exception_handler(
    request: Request, exception: Exception
) -> JSONResponse:
    logger.exception(
        msg=f"Exception thrown for request: {request.method} - {request.url}",
        exc_info=exception,
    )
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal Server Error: {exception}"},
    )


def setup_application_insights(app, settings: Settings):
    configure_azure_monitor(
        connection_string=settings.app_insights_connection_string.get_secret_value()
    )

    FastAPIInstrumentor.instrument_app(app)


def create_app() -> FastAPI:
    """
    Factory method to create a FastAPI instance.

    :return: FastAPI instance
    """
    load_dotenv()
    version = os.getenv("APP_VERSION", "0.0.0")

    app = FastAPI(version=version)
    app = setup_dependency_container(app, packages=["src.api"])

    settings = app.container.settings()
    if settings.app_insights_enabled:
        setup_application_insights(app, settings)

    app.include_router(api_router)

    app.add_exception_handler(Exception, catch_all_exception_handler)

    circuit_breaker_service: CircuitBreakerService = (
        app.container.circuit_breaker_service()
    )
    circuit_breaker_service.add_circuit(
        Circuit(
            "openai",
            failure_threshold=settings.circuit_failure_threshold,
            retry_timeout=settings.circuit_retry_timeout,
        )
    )

    return app
