from __future__ import annotations

from datetime import datetime
import json
from typing import Any

import requests

from ptt_tracking_api.models import Movement, QueryResult


class PttClientError(Exception):
    pass


class PttTrackingClient:
    def __init__(self, base_url: str, timeout_seconds: int = 20, session: requests.Session | None = None) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.session = session or requests.Session()

    @property
    def shipment_tracking_url(self) -> str:
        return f"{self.base_url}/ShipmentTracking"

    def query_barcode(self, barcode: str) -> QueryResult:
        response = self.session.post(
            self.shipment_tracking_url,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            data=json.dumps([barcode]),
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()
        payload = response.json()
        return self._parse_query_result(barcode=barcode, payload=payload)

    def query_barcodes(self, barcodes: list[str]) -> list[QueryResult]:
        return [self.query_barcode(barcode) for barcode in barcodes]

    def _parse_query_result(self, barcode: str, payload: Any) -> QueryResult:
        rows = payload if isinstance(payload, list) else payload.get("value", [])
        if not rows or not isinstance(rows[0], dict):
            raise PttClientError("PTT API bos veya beklenmeyen bir yanit dondu.")

        item = rows[0]
        message = _clean(item.get("errorMessage"))
        found = bool(item.get("errorState")) and not _is_not_found_message(message)

        if not found:
            return QueryResult(
                barcode=barcode,
                found=False,
                status=message or "Kayit bulunamadi",
                sender="",
                receiver="",
                origin="",
                destination="",
                accept_date="",
                movements=[],
                error=message or "Kayit bulunamadi",
            )

        kabul = item.get("kabul") or {}
        hareketler = [movement for movement in (item.get("hareketDongu") or []) if isinstance(movement, dict)]
        hareketler.sort(key=_movement_sort_key, reverse=True)

        movements = [
            Movement(
                date=_movement_date_text(movement),
                action=_clean(movement.get("aciklama"))
                or _clean(movement.get("islem_turu"))
                or _clean(movement.get("islem_detay")),
                location=" / ".join(
                    part
                    for part in [
                        _clean(movement.get("il")),
                        _clean(movement.get("ilce")),
                        _clean(movement.get("isyeri")),
                    ]
                    if part
                ),
                detail=_clean(movement.get("islem_detay")),
            )
            for movement in hareketler
        ]

        status = (
            _clean((item.get("sondurum") or {}).get("son_durum_aciklama"))
            or (movements[0].action if movements else "")
            or "Durum bilgisi yok"
        )

        return QueryResult(
            barcode=barcode,
            found=True,
            status=status,
            sender=_clean(kabul.get("gonderici")),
            receiver=_clean(kabul.get("alici")),
            origin=_clean(kabul.get("kabul_isyeri")),
            destination=_clean(kabul.get("alici_adres")),
            accept_date=_format_date_from_int(kabul.get("kabul_tarihi")),
            movements=movements,
            error="",
        )


def _movement_date_text(movement: dict[str, Any]) -> str:
    date_text = _clean(movement.get("tarih")) or _format_date_from_int(movement.get("intTarih"))
    time_text = _clean(movement.get("saat")) or _format_time_from_int(movement.get("intSaat"))
    if date_text and time_text:
        return f"{date_text} {time_text}"
    return date_text or time_text


def _movement_sort_key(movement: dict[str, Any]) -> float:
    int_date = movement.get("intTarih")
    int_time = movement.get("intSaat")
    if isinstance(int_date, (int, float)) and isinstance(int_time, (int, float)):
        try:
            year = int(int_date) // 10000
            month = (int(int_date) % 10000) // 100
            day = int(int_date) % 100
            hour = int(int_time) // 1000000
            minute = (int(int_time) % 1000000) // 10000
            second = (int(int_time) % 10000) // 100
            return datetime(year, month, day, hour, minute, second).timestamp()
        except ValueError:
            pass

    date_text = _clean(movement.get("tarih"))
    time_text = _clean(movement.get("saat"))
    if not date_text:
        return 0.0

    for pattern in ("%d.%m.%Y %H:%M:%S", "%d/%m/%Y %H:%M:%S", "%d-%m-%Y %H:%M:%S"):
        try:
            parsed = datetime.strptime(f"{date_text} {time_text or '00:00:00'}", pattern)
            return parsed.timestamp()
        except ValueError:
            continue
    return 0.0


def _format_date_from_int(raw: Any) -> str:
    try:
        value = str(int(float(raw))).zfill(8)
        return f"{value[6:8]}.{value[4:6]}.{value[0:4]}"
    except (TypeError, ValueError):
        return ""


def _format_time_from_int(raw: Any) -> str:
    try:
        value = int(float(raw))
        hour = value // 1000000
        minute = (value % 1000000) // 10000
        second = (value % 10000) // 100
        return f"{hour:02d}:{minute:02d}:{second:02d}"
    except (TypeError, ValueError):
        return ""


def _is_not_found_message(message: str) -> bool:
    upper = message.upper()
    return (
        "KAYIT YOK" in upper
        or "BARKOD HATALI" in upper
        or "GONDERI BULUNAMADI" in upper
        or "GONDERI BULUNMAMAKTADIR" in upper
        or "BULUNAMADI" in upper
    )


def _clean(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""
