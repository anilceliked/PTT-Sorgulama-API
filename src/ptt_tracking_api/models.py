from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Movement:
    date: str
    action: str
    location: str
    detail: str


@dataclass(slots=True)
class QueryResult:
    barcode: str
    found: bool
    status: str
    sender: str
    receiver: str
    origin: str
    destination: str
    accept_date: str
    movements: list[Movement]
    error: str
