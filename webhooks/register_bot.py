import logging
from fastapi import APIRouter, Request
from client import call
from storage import load_config, save_config
from config import EVENT_WEBHOOK

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

router = APIRouter()

@router.post("/")
async def register_bot(request: Request):

    body = await request.json()
    bot_params = body.get("bot_result")

    if not bot_params:
        return {"status": "error", "message": "bot_result is required"}

    apps = load_config()
    if not apps:
        return {"status": "error", "message": "No OAuth config found"}

    app_token, cfg = next(iter(apps.items()))
    auth = cfg.get("AUTH")

    # ОБЯЗАТЕЛЬНО
    bot_params["CLIENT_ID"] = ""
    bot_params["EVENT_HANDLER"] = EVENT_WEBHOOK

    result = await call("imbot.register", bot_params, auth)

    bot_id = result.get("result")
    if not bot_id:
        return {"status": "error", "bitrix_response": result}

    cfg["BOT_ID"] = bot_id
    save_config(apps)

    logging.info(f"✅ Бот зарегистрирован: {bot_id}")

    return {
        "status": "ok",
        "bot_id": bot_id,
        "bitrix_response": result
    }