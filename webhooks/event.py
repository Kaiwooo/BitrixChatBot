# webhooks/event.py
import logging
from fastapi import APIRouter, Request
from client import call
from storage import load_config

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

router = APIRouter()

@router.post("/")
async def event(request: Request):
    raw = await request.body()
    logging.info(f"RAW EVENT BODY: {raw.decode(errors='ignore')}")

    try:
        data = await request.json()
    except Exception:
        logging.error("❌ Не удалось распарсить тело события как JSON")
        return {"status": "error", "msg": "invalid json"}

    event_type = data.get("event")
    params = data.get("data", {}).get("PARAMS", {})
    auth = data.get("auth")
    if not auth:
        logging.error("❌ Auth не найден в событии")
        return {"status": "error", "msg": "auth not found"}

    apps = load_config()
    app_entry = apps.get(auth.get("application_token"))
    if not app_entry:
        logging.warning("⚠️ Приложение не найдено в конфиге, добавим временно")
        app_entry = {"AUTH": auth}

    bot_id = app_entry.get("BOT_ID")
    dialog_id = params.get("DIALOG_ID")
    message_text = params.get("MESSAGE")

    # Обрабатываем событие нового сообщения для бота
    if event_type == "ONIMBOTMESSAGEADD" and bot_id and dialog_id and message_text:
        # Простое эхо
        reply_text = f"Echo: {message_text}"
        logging.info(f"✅ Отправляем сообщение: {reply_text}")
        await call("imbot.message.add", {
            "DIALOG_ID": dialog_id,
            "MESSAGE": reply_text
        }, auth)

    # Обработка присоединения бота к чату / Open Line
    elif event_type == "ONIMBOTJOINCHAT" and bot_id and dialog_id:
        welcome = "Привет! Я EchoBot. Напишите что-нибудь, и я повторю это."
        logging.info(f"✅ Отправляем приветственное сообщение в чат {dialog_id}")
        await call("imbot.message.add", {
            "DIALOG_ID": dialog_id,
            "MESSAGE": welcome
        }, auth)

    # Другие события можно логировать
    else:
        logging.info(f"ℹ️ Получено событие: {event_type}")

    return {"status": "ok"}