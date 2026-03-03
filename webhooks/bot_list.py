import logging
from fastapi import APIRouter
from client.call import call
from storage import load_config
from utils.logging_helper import log_dict

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("")
async def bot_list():
    apps = load_config()
    if not apps:
        return {"status": "error", "message": "No OAuth config found"}

    app_token, cfg = next(iter(apps.items()))
    auth = cfg  # cfg уже хранит auth как словарь
    result = await call("imbot.bot.list", {}, auth)

    log_dict(logger, result)

    return result