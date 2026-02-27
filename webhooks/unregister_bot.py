import logging
from fastapi import APIRouter, Request
from client import call
from storage import load_config

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

router = APIRouter()

@router.post("/")
async def unregister_bot(request: Request):
    try:
        body = await request.json()
    except Exception:
        return {"status": "error", "message": "Invalid JSON"}

    bot_id = body.get("bot_id")

    if not bot_id:
        return {"status": "error", "message": "bot_id is required"}

    apps = load_config()
    if not apps:
        return {"status": "error", "message": "No OAuth config found"}

    # Берём первый токен
    app_token, cfg = next(iter(apps.items()))
    auth = cfg.get("AUTH")

    payload = {
        "BOT_ID": bot_id,
        "CLIENT_ID": ""
    }

    result = await call("imbot.unregister", payload, auth)

    return {
        "status": "ok",
        "bot_id": bot_id,
        "bitrix_result": result
    }