# PTT Tracking API

🚀 Barkod numarası ile PTT gönderi sorgulamak için oluşturulmuş, sade ve üretime uygun bir `FastAPI` servisidir.

> Geliştirici: **Anıl Çelik**  
> GitHub: **[@anilceliked](https://github.com/anilceliked)**

Bu repo yalnızca PTT sorgulama işlevine odaklanır:
- Tek barkod sorgulama
- Toplu barkod sorgulama
- Temiz servis mimarisi
- Swagger dokümantasyonu
- Test edilebilir API yapısı

## ✨ Özellikler

- `GET /api/v1/shipments/{barcode}` ile tek barkod sorgulama
- `POST /api/v1/shipments/query` ile toplu barkod sorgulama
- PTT resmî servisinden gelen durum, gönderici, alıcı ve hareket bilgilerini normalize etme
- `.env` tabanlı konfigürasyon
- `pytest` ile temel test kapsamı

## 🧱 Proje Yapısı

```text
src/ptt_tracking_api/
  api.py
  client.py
  config.py
  main.py
  models.py
  schemas.py
tests/
```

## ⚙️ Kurulum

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e .[dev]
```

## ▶️ Çalıştırma

```bash
uvicorn ptt_tracking_api.main:app --reload
```

Dokümantasyon:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## 🔐 Ortam Değişkenleri

`.env.example` dosyasını referans alabilirsiniz.

- `PTT_API_BASE_URL`: Varsayılan `https://api.ptt.gov.tr/api`
- `PTT_API_TIMEOUT_SECONDS`: Varsayılan `20`

## 📡 Endpointler

### `GET /health`

Servis durumunu kontrol eder.

### `GET /api/v1/shipments/{barcode}`

Tek barkod için PTT sorgusu yapar.

Örnek:

```bash
curl http://127.0.0.1:8000/api/v1/shipments/RR123456789TR
```

### `POST /api/v1/shipments/query`

Birden fazla barkodu tek istekte sorgular.

Örnek istek:

```json
{
  "barcodes": ["RR123456789TR", "1234567890123"]
}
```

Örnek `curl`:

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/shipments/query" \
  -H "Content-Type: application/json" \
  -d "{\"barcodes\":[\"RR123456789TR\",\"1234567890123\"]}"
```

## 🧪 Test

```bash
pytest
```

## 📝 Notlar

- Bu servis PTT tarafındaki resmî servise bağlıdır.
- PTT servisinde değişiklik olursa istemci katmanının güncellenmesi gerekebilir.
- Proje bilerek dar tutuldu; PDF ayıklama, GUI ve masaüstü uygulama kodları dahil edilmedi.

## 👤 Geliştirici

**Anıl Çelik**  
GitHub: [@anilceliked](https://github.com/anilceliked)
