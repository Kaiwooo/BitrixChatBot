import logging
from fastapi import APIRouter, Request
from client.call import call
from storage import load_config

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

router = APIRouter()

@router.post("")
async def unregister_bot(request: Request):
    try:
        bot_params = await request.json()
    except Exception:
        return {"status": "error", "message": "Invalid JSON"}

    bot_id = bot_params.get("bot_id")
    if not bot_params:
        return {"status": "error", "message": "bot_id is required"}

    apps = load_config()
    if not apps:
        return {"status": "error", "message": "No OAuth config found"}

    app_token, cfg = next(iter(apps.items()))
    auth = cfg.get("AUTH")

    result = await call("imbot.unregister", bot_params, auth)

    logging.info(f"Bot ID: {bot_id}, Bitrix response: {result}")

    return {
        "Status": "Success",
        "Bot_ID": bot_id,
        "Bitrix_Result": result
    }