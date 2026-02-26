import logging
from fastapi import FastAPI, Request
from b24pysdk import BitrixApp, BitrixTokenLocal, Client
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Словарь для хранения токенов по домену
TOKENS = {}

# ------------------------
# Установка приложения
# ------------------------
@app.post("/install")
async def install(request: Request):
    form = await request.form()
    data = dict(form)

    # Получаем auth и client_id/client_secret
    auth = {k.replace("auth[", "").replace("]", ""): v for k, v in data.items() if k.startswith("auth[")}

    domain = auth.get("domain")
    TOKENS[domain] = auth
    logger.info(f"INSTALL DATA: {data}")
    logger.info(f"SAVED AUTH: {auth}")

    # Создаём BitrixApp
    bitrix_app = BitrixApp(
        client_id=auth.get("client_id"),
        client_secret=auth.get("client_secret")
    )

    # Создаём локальный токен
    bitrix_token = BitrixTokenLocal(
        auth_token=auth.get("access_token"),
        refresh_token=auth.get("refresh_token"),
        bitrix_app=bitrix_app,
        expires_in=int(auth.get("expires_in", 3600))
    )

    # Клиент REST API v3
    client = Client(bitrix_token, prefer_version=3)

    # Регистрируем бота через call()
    result = await client.call(
        "imbot.register",
        {
            "TYPE": "B",
            "CODE": "echo_bot_python",
            "EVENT_MESSAGE_ADD": f"https://{domain}/event",
            "PROPERTIES": {
                "NAME": "Echo Bot",
                "COLOR": "AQUA",
            },
        }
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

    # Определяем домен
    domain = data.get("auth[domain]") or data.get("data", {}).get("DOMAIN")
    if not domain or domain not in TOKENS:
        logger.warning(f"No auth for domain: {domain}")
        return {"result": "no auth"}

    auth = TOKENS[domain]

    # Создаём BitrixApp + Token + Client
    bitrix_app = BitrixApp(
        client_id=auth.get("client_id"),
        client_secret=auth.get("client_secret")
    )
    bitrix_token = BitrixTokenLocal(
        auth_token=auth.get("access_token"),
        refresh_token=auth.get("refresh_token"),
        bitrix_app=bitrix_app,
        expires_in=int(auth.get("expires_in", 3600))
    )
    client = Client(bitrix_token, prefer_version=3)

    # Эхо на входящее сообщение
    if data.get("event") == "ONIMBOTMESSAGEADD":
        msg_data = data.get("data", {})
        dialog_id = msg_data.get("DIALOG_ID")
        message_text = msg_data.get("MESSAGE")

        if dialog_id and message_text:
            response = await client.call(
                "imbot.message.add",
                {
                    "DIALOG_ID": dialog_id,
                    "MESSAGE": message_text
                }
            )
            logger.info(f"Echoed message to {dialog_id}: {message_text}, response: {response}")

    return {"result": "ok"}