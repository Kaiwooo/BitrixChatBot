import httpx
import logging
from storage import BITRIX_AUTH

async def call(method: str, payload: dict | None = None):
    auth = BITRIX_AUTH.get("default")
    if not auth:
        logging.error("❌ Bitrix не установлен")
        return None

    url = auth["client_endpoint"].rstrip("/") + f"/{method}.json"
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            url,
            params={"auth": auth["access_token"]},
            json=payload or {},
            timeout=10
        )

    data = resp.json()
    logging.info(f"[BITRIX] {method} → {data}")
    return data