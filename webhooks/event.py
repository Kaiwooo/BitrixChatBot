from fastapi import APIRouter, Request
import logging
from client import call

router = APIRouter()

@router.post("/event")
async def bitrix_event(request: Request):
    data = await request.json()
    logging.info("Получен webhooks от Bitrix")
    logging.info(data)

    # Эхо-ответ: если есть CHAT_ID и MESSAGE
    chat_id = data.get("data", {}).get("PARAMS", {}).get("CHAT_ID")
    message = data.get("data", {}).get("PARAMS", {}).get("MESSAGE")

    if chat_id and message:
        await call("im.message.add", {"CHAT_ID": chat_id, "MESSAGE": f"Echo: {message}"})

    return {"status": "ok"}