import logging
from fastapi import APIRouter, Request
from client.call import call
from storage import load_config
from utils.logging_helper import log_dict

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("")
async def register_bot(request: Request):
    apps = load_config()
    if not apps:
        return {"Status": "Error", "Message": "No OAuth config found"}
    try:
        bot_params = await request.json()
    except Exception:
        return {"Status": "Error", "Message": "Invalid JSON"}

    if not bot_params:
        return {"Status": "Error", "Message": "Empty body"}

    app_token, cfg = next(iter(apps.items()))
    auth = cfg  # cfg уже хранит auth как словарь

    result = await call("imbot.register", bot_params, auth)
    bot_id = result.get("result")
    if not bot_id:
        return {result}

    log_dict(logger, result)
    return result