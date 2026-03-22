from fastapi import FastAPI

from ptt_tracking_api.api import router


app = FastAPI(
    title="PTT Tracking API",
    version="0.1.0",
    description="PTT barkod sorgulama servisi.",
    contact={
        "name": "Anıl Çelik",
        "url": "https://github.com/anilceliked",
    },
)
app.include_router(router)
