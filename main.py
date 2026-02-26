import logging
from fastapi import FastAPI, Request
from b24pysdk import BitrixApp
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Словарь для хранения токенов (ключ — domain)
TOKENS = {}

# ------------------------
# Установка приложения
# ------------------------
@app.post("/install")
async def install(request: Request):
    # Обработка запроса
    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        data = await request.json()
    else:
        form = await request.form()
        data = dict(form)

    # Парсим auth
    auth = {k.replace("auth[", "").replace("]", ""): v for k, v in data.items() if k.startswith("auth[")}

    domain = auth.get("domain")
    TOKENS[domain] = auth
    logger.info(f"INSTALL DATA: {data}")
    logger.info(f"SAVED AUTH: {auth}")

    # Создаём BitrixApp с обязательными client_id и client_secret
    bx = BitrixApp(
        client_id=auth.get("client_id"),
        client_secret=auth.get("client_secret")
    )

    # Передаём access/refresh токены
    bx.set_auth(
        domain=auth.get("domain"),
        access_token=auth.get("access_token"),
        refresh_token=auth.get("refresh_token")
    )

    # Регистрируем бота
    result = await bx.call(
        "imbot.register",
        {
            "TYPE": "B",
            "CODE": "echo_bot_python",
            "EVENT_MESSAGE_ADD": f"https://{domain}/event",
            "PROPERTIES": {
                "NAME": "Echo Bot",
                "COLOR": "AQUA",
            },
        },
    )

    logger.info(f"BOT REGISTER RESULT: {result}")
    return {"result": "installed"}


# ------------------------
# Обработка событий
# ------------------------
@app.post("/event")
async def event_handler(request: Request):
    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        data = await request.json()
    else:
        form = await request.form()
        data = dict(form)
        if "data" in data:
            data["data"] = json.loads(data["data"])

    logger.info(f"EVENT DATA: {data}")

    # Определяем domain
    domain = data.get("auth[domain]") or data.get("data", {}).get("DOMAIN")
    if not domain or domain not in TOKENS:
        logger.warning(f"No auth for domain: {domain}")
        return {"result": "no auth"}

    auth = TOKENS[domain]

    # Создаём BitrixApp с auth
    bx = BitrixApp()
    bx.set_auth(
        domain=auth.get("domain"),
        access_token=auth.get("access_token"),
        refresh_token=auth.get("refresh_token"),
        client_id=auth.get("client_id"),
        client_secret=auth.get("client_secret"),
    )

    # Обработка входящего сообщения
    if data.get("event") == "ONIMBOTMESSAGEADD":
        msg_data = data.get("data", {})
        dialog_id = msg_data.get("DIALOG_ID")
        message_text = msg_data.get("MESSAGE")

        if dialog_id and message_text:
            await bx.call(
                "imbot.message.add",
                {
                    "DIALOG_ID": dialog_id,
                    "MESSAGE": message_text
                },
            )
            logger.info(f"Echoed message to {dialog_id}: {message_text}")

    return {"result": "ok"}