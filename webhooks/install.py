import logging
from fastapi import APIRouter, Request
from storage import BITRIX_AUTH

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

router = APIRouter()

@router.post("/install")
async def install(request: Request):
    raw = await request.body()
    logging.info(f"RAW INSTALL: {raw.decode(errors='ignore')}")

    data = {}
    try:
        data = await request.json()
    except:
        form = await request.form()
        data = dict(form)

    auth = {}
    for k, v in data.items():
        if k.startswith("auth[") and k.endswith("]"):
            auth[k[5:-1]] = v

    if auth:
        BITRIX_AUTH["default"] = auth
        logging.info("✅ OAuth сохранён")

    return {"status": "ok"}