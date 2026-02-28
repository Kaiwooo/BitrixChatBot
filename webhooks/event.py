# webhooks/event.py
import logging
from fastapi import APIRouter, Request
from client.call import call

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

router = APIRouter()

@router.post("")
async def event(request: Request):
    # Получаем сырой body для логов
    raw = await request.body()
    logging.info(f"RAW EVENT BODY: {raw.decode(errors='ignore')}")

    # Пробуем распарсить JSON, иначе form-data
    try:
        data = await request.json()
    except Exception:
        form = await request.form()
        data = dict(form)

    logging.info(f"Parsed DATA: {data}")

    # Извлекаем auth
    auth = data.get("auth")
    if not isinstance(auth, dict):
        logging.error("❌ Auth не найден или некорректен")
        return {"status": "error", "msg": "auth not found"}

    # Тип события
    event_type = data.get("event")
    data_section = data.get("data") or {}

    # Получаем id бота и данные сообщения
    bot_id = data_section.get("BOT_ID") or data.get("data[BOT_ID]")
    dialog_id = data_section.get("DIALOG_ID")
    message_text = data_section.get("MESSAGE")

    # Обрабатываем событие удаления бота
    if event_type == "ONIMBOTDELETE":
        logging.info(f"🤖 Bot deleted from portal: {bot_id}")
        return {"status": "ok"}

    # Эхо-сообщение при добавлении сообщения боту
    if event_type == "ONIMBOTMESSAGEADD" and dialog_id and message_text:
        reply_text = f"Echo: {message_text}"
        logging.info(f"✅ Отправляем сообщение: {reply_text}")
        try:
            await call("imbot.message.add", {"DIALOG_ID": dialog_id, "MESSAGE": reply_text}, auth)
        except Exception as e:
            logging.error(f"❌ Ошибка отправки сообщения: {e}")

    # Приветственное сообщение при присоединении к чату / Open Line
    elif event_type == "ONIMBOTJOINCHAT" and dialog_id:
        welcome = "Привет! Я EchoBot. Напишите что-нибудь, и я повторю это."
        logging.info(f"✅ Отправляем приветствие в чат {dialog_id}")
        try:
            await call("imbot.message.add", {"DIALOG_ID": dialog_id, "MESSAGE": welcome}, auth)
        except Exception as e:
            logging.error(f"❌ Ошибка отправки приветствия: {e}")

    # Все остальные события логируем
    else:
        logging.info(f"ℹ️ Получено событие: {event_type}")

    return {"status": "ok"}