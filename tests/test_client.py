from ptt_tracking_api.client import PttClientError, PttTrackingClient


def test_query_result_is_parsed_for_found_record() -> None:
    client = PttTrackingClient(base_url="https://example.com")
    payload = [
        {
            "errorState": True,
            "errorMessage": "",
            "kabul": {
                "gonderici": "Mahkeme",
                "alici": "Ali Veli",
                "kabul_isyeri": "Ankara",
                "alici_adres": "İstanbul",
                "kabul_tarihi": 20260320,
            },
            "sondurum": {"son_durum_aciklama": "Teslim edildi"},
            "hareketDongu": [
                {
                    "intTarih": 20260321,
                    "intSaat": 15304500,
                    "aciklama": "Teslim edildi",
                    "islem_detay": "Alıcıya teslim",
                    "il": "İstanbul",
                    "ilce": "Kadıköy",
                    "isyeri": "Dağıtım",
                }
            ],
        }
    ]

    result = client._parse_query_result(barcode="RR123456789TR", payload=payload)

    assert result.found is True
    assert result.status == "Teslim edildi"
    assert result.sender == "Mahkeme"
    assert result.movements[0].location == "İstanbul / Kadıköy / Dağıtım"


def test_query_result_handles_not_found_record() -> None:
    client = PttTrackingClient(base_url="https://example.com")
    payload = [{"errorState": False, "errorMessage": "Gönderi bulunamadı"}]

    result = client._parse_query_result(barcode="RR000000000TR", payload=payload)

    assert result.found is False
    assert result.error == "Gönderi bulunamadı"


def test_query_result_rejects_empty_payload() -> None:
    client = PttTrackingClient(base_url="https://example.com")

    try:
        client._parse_query_result(barcode="RR000000000TR", payload=[])
    except PttClientError as exc:
        assert "beklenmeyen" in str(exc)
    else:
        raise AssertionError("PttClientError bekleniyordu")
