from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from requests import HTTPError, RequestException

from ptt_tracking_api.client import PttClientError, PttTrackingClient
from ptt_tracking_api.config import Settings, get_settings
from ptt_tracking_api.schemas import (
    BatchShipmentQueryRequest,
    BatchShipmentQueryResponse,
    HealthResponse,
    ShipmentQueryResponse,
)


router = APIRouter()


def get_client(settings: Settings = Depends(get_settings)) -> PttTrackingClient:
    return PttTrackingClient(
        base_url=settings.api_base_url,
        timeout_seconds=settings.api_timeout_seconds,
    )


@router.get("/health", response_model=HealthResponse, tags=["system"])
def healthcheck() -> HealthResponse:
    return HealthResponse(status="ok")


@router.get("/api/v1/shipments/{barcode}", response_model=ShipmentQueryResponse, tags=["shipments"])
def query_shipment(barcode: str, client: PttTrackingClient = Depends(get_client)) -> ShipmentQueryResponse:
    try:
        return ShipmentQueryResponse.model_validate(_serialize_query_result(client.query_barcode(barcode)))
    except HTTPError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"PTT HTTP hatasi: {exc}") from exc
    except (RequestException, PttClientError) as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc


@router.post("/api/v1/shipments/query", response_model=BatchShipmentQueryResponse, tags=["shipments"])
def query_shipments(
    request: BatchShipmentQueryRequest,
    client: PttTrackingClient = Depends(get_client),
) -> BatchShipmentQueryResponse:
    results: list[ShipmentQueryResponse] = []
    for barcode in request.barcodes:
        try:
            result = client.query_barcode(barcode)
            results.append(ShipmentQueryResponse.model_validate(_serialize_query_result(result)))
        except (HTTPError, RequestException, PttClientError) as exc:
            results.append(
                ShipmentQueryResponse(
                    barcode=barcode,
                    found=False,
                    status="PTT error",
                    error=str(exc),
                    movements=[],
                )
            )

    return BatchShipmentQueryResponse(results=results)


def _serialize_query_result(result: object) -> dict:
    return {
        "barcode": result.barcode,
        "found": result.found,
        "status": result.status,
        "sender": result.sender,
        "receiver": result.receiver,
        "origin": result.origin,
        "destination": result.destination,
        "accept_date": result.accept_date,
        "movements": [
            {
                "date": movement.date,
                "action": movement.action,
                "location": movement.location,
                "detail": movement.detail,
            }
            for movement in result.movements
        ],
        "error": result.error,
    }
