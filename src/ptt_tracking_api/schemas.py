from pydantic import BaseModel, Field


class MovementResponse(BaseModel):
    date: str = ""
    action: str = ""
    location: str = ""
    detail: str = ""


class ShipmentQueryResponse(BaseModel):
    barcode: str
    found: bool
    status: str
    sender: str = ""
    receiver: str = ""
    origin: str = ""
    destination: str = ""
    accept_date: str = ""
    movements: list[MovementResponse] = Field(default_factory=list)
    error: str = ""


class BatchShipmentQueryRequest(BaseModel):
    barcodes: list[str] = Field(min_length=1, max_length=500)


class BatchShipmentQueryResponse(BaseModel):
    results: list[ShipmentQueryResponse]


class HealthResponse(BaseModel):
    status: str
