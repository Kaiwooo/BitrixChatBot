import logging, json
from fastapi import APIRouter, Request
from storage import load_config, save_config

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

router = APIRouter()

@router.post("")
async def install(request: Request):
    try:
        data = await request.json()
    except Exception:
        form = await request.form()
        data = dict(form)

    logging.info("INSTALL JSON:\n%s", json.dumps(data, indent=2, ensure_ascii=False))

    # Извлекаем auth
    auth = {}
    for k, v in data.items():
        if k.startswith("auth[") and k.endswith("]"):
            auth[k[5:-1]] = v

    if not auth:
        logging.error("❌ Auth не найден")
        return {"status": "error", "msg": "auth not found"}

    apps = load_config()
    apps[auth["application_token"]] = auth  # вместо {"AUTH": auth}
    save_config(apps)

    logging.info("✅ OAuth сохранён в конфиг")

    return {"status": "ok"}