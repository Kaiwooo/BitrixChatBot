import logging
from fastapi import APIRouter
from client.call import call
from storage import load_config

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

router = APIRouter()

@router.post("")
async def unregister_bot():
    apps = load_config()
    if not apps:
        return {"status": "error", "message": "No OAuth config found"}

    app_token, cfg = next(iter(apps.items()))
    auth = cfg  # cfg уже хранит auth как словарь
    result = await call("imbot.bot.list", {}, auth)

    logging.info(f"Bitrix response: {result}")

    return {
        "Status": "Success",
        "Bitrix_Result": result
    }