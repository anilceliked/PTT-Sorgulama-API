from fastapi.testclient import TestClient

from ptt_tracking_api.main import app
from ptt_tracking_api.models import Movement, QueryResult


class StubClient:
    def query_barcode(self, barcode: str) -> QueryResult:
        return QueryResult(
            barcode=barcode,
            found=True,
            status="Teslim edildi",
            sender="Mahkeme",
            receiver="Ali Veli",
            origin="Ankara",
            destination="İstanbul",
            accept_date="20.03.2026",
            movements=[
                Movement(
                    date="21.03.2026 15:30:45",
                    action="Teslim edildi",
                    location="İstanbul / Kadıköy / Dağıtım",
                    detail="Alıcıya teslim",
                )
            ],
            error="",
        )


def test_healthcheck() -> None:
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_query_shipment_endpoint() -> None:
    from ptt_tracking_api.api import get_client

    app.dependency_overrides[get_client] = lambda: StubClient()
    client = TestClient(app)

    response = client.get("/api/v1/shipments/RR123456789TR")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["barcode"] == "RR123456789TR"


def test_query_shipments_batch_endpoint() -> None:
    from ptt_tracking_api.api import get_client

    app.dependency_overrides[get_client] = lambda: StubClient()
    client = TestClient(app)

    response = client.post(
        "/api/v1/shipments/query",
        json={"barcodes": ["RR123456789TR", "1234567890123"]},
    )

    app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert len(payload["results"]) == 2
    assert payload["results"][0]["found"] is True
