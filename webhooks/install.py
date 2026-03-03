import logging
from fastapi import APIRouter, Request
from storage import load_config, save_config
from utils.logging_helper import log_dict

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("")
async def install(request: Request):
    try:
        data = await request.json()
    except Exception:
        form = await request.form()
        data = dict(form)

    log_dict(logger, data)

    # Извлекаем auth
    auth = {}
    for k, v in data.items():
        if k.startswith("auth[") and k.endswith("]"):
            auth[k[5:-1]] = v

    if not auth:
        logging.error("❌ Auth не найден")
        return

    apps = load_config()
    apps[auth["application_token"]] = auth  # вместо {"AUTH": auth}
    save_config(apps)

    logging.info("✅ OAuth сохранён в конфиг")

    return