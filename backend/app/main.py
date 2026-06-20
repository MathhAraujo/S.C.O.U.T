from fastapi import FastAPI

from app.api.v1 import api_router

app = FastAPI(title="Injury Detection System", version="0.1.0")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(api_router)
