import logging

import requests
from urllib.parse import urlparse

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status


from src.dependency_container import DependencyContainer
from src.services.circuit_breaker_service import CircuitBreakerService
from src.settings import Settings

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/openai/{path:path}")
@router.post("/openai/{path:path}")
@router.put("/openai/{path:path}")
@router.delete("/openai/{path:path}")
@inject
async def openai(
    request: Request,
    circuit_breaker_service: CircuitBreakerService = Depends(
        Provide[DependencyContainer.circuit_breaker_service]
    ),
    settings: Settings = Depends(Provide[DependencyContainer.settings]),
):
    downstream_response = await circuit_breaker_service.execute(
        "openai",
        function=lambda: forward_request(
            settings.primary_open_ai_host,
            settings.primary_open_ai_api_key.get_secret_value(),
            request.url.path,
            request,
        ),
        fallback_function=lambda: forward_request(
            settings.fallback_open_ai_host,
            settings.fallback_open_ai_api_key.get_secret_value(),
            request.url.path,
            request,
            False,
        ),
    )

    return Response(
        downstream_response.content,
        status_code=downstream_response.status_code,
        headers=downstream_response.headers,
    )


async def forward_request(
    openai_host, api_key, path, forwarding_request, check_status_code=True
):
    parsed_host = urlparse(openai_host)
    url = f"{parsed_host.geturl()}{path}"
    params = dict(forwarding_request.query_params)
    method = forwarding_request.method
    data = await forwarding_request.body()

    # Override headers. Prompt flow sends a large number of headers, causing the downstream to return an error.
    headers = {
        "host": parsed_host.hostname,
        "accept": forwarding_request.headers.get("accept"),
        "content-type": forwarding_request.headers.get("content-type"),
        "accept-encoding": forwarding_request.headers.get("accept-encoding"),
        "api-key": api_key,
    }

    logger.info(
        f"Making request to url: '{url}' \nParams: {params}\nMethod: {method}\nBody: {data} "
    )

    downstream_response = requests.request(
        method,
        url,
        headers=headers,
        data=data,
        params=params,
    )

    logger.info(
        f"Got response status: {downstream_response.status_code}\nBody: {downstream_response.content}"
    )

    # Only raise the exception if the main downstream API returns an error, to force the fallback mechanism.
    # If the fallback API returns an error, return this to the client as-is.
    if check_status_code and (
        downstream_response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        or downstream_response.status_code >= 500
    ):
        raise HTTPException(
            status_code=downstream_response.status_code,
            detail=downstream_response.text,
        )

    # Remove the Connection header before returning the downstream response, as it cannot be returned
    downstream_response.headers.pop("connection", None)
    return downstream_response
