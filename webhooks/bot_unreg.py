import logging
from fastapi import APIRouter, Request
from client.call import call
from storage import load_config
from utils.logging_helper import log_dict

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("")
async def unregister_bot(request: Request):
    apps = load_config()
    if not apps:
        return {"Status": "Error", "Message": "No OAuth config found"}

    try:
        bot_params = await request.json()
    except Exception:
        return {"status": "error", "message": "Invalid JSON"}

    bot_id = bot_params.get("bot_id")
    if not bot_id:
        return {"status": "error", "message": "bot_id is required"}

    app_token, cfg = next(iter(apps.items()))
    auth = cfg  # cfg уже хранит auth как словарь
    result = await call("imbot.unregister", bot_params, auth)

    log_dict(logger, result)

    return result