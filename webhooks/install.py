# webhooks/install.py
import json
from fastapi import APIRouter, Request
from client import call
from storage import load_config, save_config
from config import EVENT_WEBHOOK

router = APIRouter()


@router.post("/")
async def install(request: Request):
    # Попытка получить JSON, fallback на form
    try:
        data = await request.json()
    except json.JSONDecodeError:
        form = await request.form()
        data = dict(form)

    # auth может быть JSON-строкой
    auth_raw = data.get("auth")
    if isinstance(auth_raw, str):
        try:
            auth = json.loads(auth_raw)
        except json.JSONDecodeError:
            return {"status": "error", "message": "auth is invalid JSON"}
    elif isinstance(auth_raw, dict):
        auth = auth_raw
    else:
        return {"status": "error", "message": "auth missing or invalid"}

    # язык
    lang_raw = data.get("data")
    if isinstance(lang_raw, str):
        try:
            lang_data = json.loads(lang_raw)
        except json.JSONDecodeError:
            lang_data = {}
    elif isinstance(lang_raw, dict):
        lang_data = lang_raw
    else:
        lang_data = {}
    lang = lang_data.get("LANGUAGE_ID", "en")

    apps = load_config()
    handler_url = EVENT_WEBHOOK

    # Регистрация бота
    bot_result = await call("imbot.register", {
        "CODE": "echobot",
        "TYPE": "O",
        "EVENT_MESSAGE_ADD": handler_url,
        "EVENT_WELCOME_MESSAGE": handler_url,
        "EVENT_BOT_DELETE": handler_url,
        "OPENLINE": "Y",
        "PROPERTIES": {
            "NAME": f"My Python Chatbot EchoBot {len(apps)+1}",
            "COLOR": "GREEN",
            "EMAIL": "test@test.ru",
            "WORK_POSITION": "My first echo bot"
        }
    }, auth)

    bot_id = bot_result.get("result")
    if not bot_id:
        return {"status": "error", "message": "failed to register bot", "details": bot_result}

    # Регистрация команд
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

    # Подписка на событие OnAppUpdate
    await call("event.bind", {"EVENT":"OnAppUpdate","HANDLER":handler_url}, auth)

    # Сохранение конфигурации
    apps[auth["application_token"]] = {
        "BOT_ID": bot_id,
        "COMMANDS": commands,
        "LANGUAGE_ID": lang,
        "AUTH": auth
    }
    save_config(apps)

    return {"status": "ok", "bot_id": bot_id, "commands": commands}