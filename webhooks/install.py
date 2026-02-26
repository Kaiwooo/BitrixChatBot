# webhooks/install.py
import logging
from fastapi import APIRouter, Request
from client import call
from storage import load_config, save_config
from config import EVENT_WEBHOOK

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

router = APIRouter()

@router.post("/")
async def install(request: Request):
    raw = await request.body()
    logging.info(f"RAW INSTALL BODY: {raw.decode(errors='ignore')}")

    # Попробуем распарсить JSON, иначе form-data
    data = {}
    try:
        data = await request.json()
    except Exception:
        form = await request.form()
        data = dict(form)

    # Извлекаем auth
    auth = {}
    for k, v in data.items():
        if k.startswith("auth[") and k.endswith("]"):
            auth[k[5:-1]] = v

    if not auth:
        logging.error("❌ Auth не найден")
        return {"status": "error", "msg": "auth not found"}

    logging.info(f"✅ OAuth получен: {auth}")

    apps = load_config()
    lang = data.get("data", {}).get("LANGUAGE_ID", "en")
    handler_url = EVENT_WEBHOOK  # <-- адрес для событий сообщений

    # Регистрируем бота
    bot_result = await call("imbot.register", {
        "CODE": "echobot",
        "TYPE": "O",

        "EVENT_MESSAGE_ADD": handler_url,
        "EVENT_WELCOME_MESSAGE": handler_url,
        "EVENT_BOT_DELETE": handler_url,

        "OPENLINE": "Y",
        "NAME": "MyPythonEchoBot",
        "PROPERTIES": {
            "LAST_NAME": "BotLastName",
            "COLOR": "GREEN",
            "EMAIL": "test@test.ru",
            "PERSONAL_BIRTHDAY": "2016-03-11",
            "WORK_POSITION": "EchoBot for Open Line"
        }
    }, auth)

    bot_id = bot_result.get("result")
    if not bot_id:
        logging.error(f"❌ Не удалось зарегистрировать бота: {bot_result}")
        return {"status": "error", "msg": "bot registration failed"}

    logging.info(f"✅ Бот зарегистрирован, ID: {bot_id}")

    # Регистрируем команды бота
    commands = {}
    for cmd, title in [("echo","Echo message"), ("echoList","List of colors"), ("help","Help message")]:
        res = await call("imbot.command.register", {
            "BOT_ID": bot_id,
            "COMMAND": cmd,
            "COMMON": "Y" if cmd=="echo" else "N",
            "HIDDEN": "N",
            "EXTRANET_SUPPORT": "N",
            "LANG": [{"LANGUAGE_ID": lang, "TITLE": title, "PARAMS": ""}],
            "EVENT_COMMAND_ADD": handler_url
        }, auth)
        commands[cmd] = res.get("result")

    logging.info(f"✅ Команды зарегистрированы: {commands}")

    # Подписка на OnAppUpdate
    bind_res = await call("event.bind", {"EVENT":"OnAppUpdate","HANDLER":handler_url}, auth)
    logging.info(f"✅ Подписка на OnAppUpdate: {bind_res}")

    apps[auth["application_token"]] = {
        "BOT_ID": bot_id,
        "COMMANDS": commands,
        "LANGUAGE_ID": lang,
        "AUTH": auth
    }
    save_config(apps)
    logging.info("✅ Конфиг приложения сохранён")

    return {"status": "ok", "bot_id": bot_id, "commands": commands}