import logging
from fastapi import APIRouter, Request
from client import call
from storage import load_config, save_config

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

router = APIRouter()

@router.post("")
async def register_bot(request: Request):

    try:
        bot_params = await request.json()
    except Exception:
        return {"status": "error", "message": "Invalid JSON"}

    if not bot_params:
        return {"status": "error", "message": "Empty body"}

    apps = load_config()
    if not apps:
        return {"status": "error", "message": "No OAuth config found"}

    app_token, cfg = next(iter(apps.items()))
    auth = cfg.get("AUTH")

    # Отправляем в Bitrix ровно то, что пришло
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