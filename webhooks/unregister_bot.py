import logging
from fastapi import APIRouter, Request
from client import call
from storage import load_config, save_config

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

router = APIRouter()

@router.post("/")
async def unregister_bot(request: Request):
    body = await request.json()
    bot_id = body.get("bot_id")

    if not bot_id:
        return {"status": "error", "message": "bot_id is required"}

    apps = load_config()

    # Найдём приложение, которому принадлежит bot_id
    app_token = None
    for token, cfg in apps.items():
        if cfg.get("BOT_ID") == bot_id:
            app_token = token
            break

    if not app_token:
        return {"status": "error", "message": "bot_id not found in config"}

    # Получаем auth от этого приложения
    auth = apps[app_token]["AUTH"]

    # Удаляем бот
    payload = {
        "BOT_ID": bot_id,
        "CLIENT_ID": ""
    }
    result = await call("imbot.unregister", payload, auth)

    # Удаляем из local config
    del apps[app_token]
    save_config(apps)

    logging.info(f"Bot {bot_id} unregistered")

    return {
        "status": "ok",
        "bot_id": bot_id,
        "bitrix_result": result
    }