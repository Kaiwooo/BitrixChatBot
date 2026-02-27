import logging
from fastapi import APIRouter, Request
from storage import load_config, save_config

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

router = APIRouter()

@router.post("")
async def install(request: Request):
    raw = await request.body()
    logging.info(f"RAW INSTALL BODY: {raw.decode(errors='ignore')}")

    try:
        data = await request.json()
    except Exception:
        form = await request.form()
        data = dict(form)

    # Извлекаем auth
    auth = {}
    for k, v in data.items():
        if k.startswith("auth[") and k.endswith("]"):
            auth[k[5:-1]] = v

    if not auth:
        logging.error("❌ Auth не найден")
        return {"status": "error", "msg": "auth not found"}

    apps = load_config()
    apps[auth["application_token"]] = {
        "AUTH": auth
    }
    save_config(apps)

    logging.info("✅ OAuth сохранён в конфиг")

    return {"status": "ok"}