# webhooks/event.py
from client import call
from fastapi import APIRouter, Request
import logging

router = APIRouter()

@router.post("")
async def event(request: Request):
    raw = await request.body()
    logging.info(f"RAW EVENT BODY: {raw.decode(errors='ignore')}")

    try:
        data = await request.json()
    except Exception:
        form = await request.form()
        data = dict(form)

    # SDK хочет auth в виде словаря
    # Берём либо из data["auth"], либо из data["data[BOT][ID][AUTH]"]
    auth_keys = [k for k in data.keys() if k.startswith("auth[")]
    auth = {}
    for k in auth_keys:
        auth[k[5:-1]] = data[k]

    if not auth:
        logging.error("❌ Auth не найден")
        return {"status": "error", "msg": "auth not found"}

    event_type = data.get("event")
    params = {}
    # собираем params для сообщений
    for k, v in data.items():
        if k.startswith("data[PARAMS]"):
            key = k[len("data[PARAMS]["):-1]
            params[key] = v

    dialog_id = params.get("DIALOG_ID")
    message_text = params.get("MESSAGE")

    # Обработка события добавления сообщения
    if event_type == "ONIMBOTMESSAGEADD" and dialog_id and message_text:
        reply_text = f"Echo: {message_text}"
        logging.info(f"✅ Отправляем сообщение: {reply_text}")
        await call("imbot.message.add", {"DIALOG_ID": dialog_id, "MESSAGE": reply_text}, auth)

    elif event_type == "ONIMBOTJOINCHAT" and dialog_id:
        welcome = "Привет! Я EchoBot. Напишите что-нибудь, и я повторю это."
        logging.info(f"✅ Отправляем приветствие в чат {dialog_id}")
        await call("imbot.message.add", {"DIALOG_ID": dialog_id, "MESSAGE": welcome}, auth)

    else:
        logging.info(f"ℹ️ Получено событие: {event_type}")

    return {"status": "ok"}