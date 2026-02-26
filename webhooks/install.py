# webhooks/install.py
from fastapi import APIRouter, Request
from client import call
from storage import load_config, save_config
from config import EVENT_WEBHOOK

router = APIRouter()

@router.post("/")
async def install(request: Request):
    data = await request.json()
    auth = data.get("auth")
    lang = data.get("data", {}).get("LANGUAGE_ID", "en")
    apps = load_config()
    handler_url = EVENT_WEBHOOK

    # Register Bot
    bot_result = await call("imbot.register", {
        "CODE": "echobot",
        "TYPE": "O",
        "EVENT_MESSAGE_ADD": handler_url,
        "EVENT_WELCOME_MESSAGE": handler_url,
        "EVENT_BOT_DELETE": handler_url,
        "OPENLINE": "Y",
        'CLIENT_ID': '',
        "PROPERTIES": {
            "NAME": f"My Python Chatbot EchoBot {len(apps)+1}",
            "COLOR": "GREEN",
            "EMAIL": "test@test.ru",
            "WORK_POSITION": "My first echo bot"
        }
    }, auth)
    bot_id = bot_result.get("result")

    # Register Commands
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

    # Bind OnAppUpdate
    await call("event.bind", {"EVENT":"OnAppUpdate","HANDLER":handler_url}, auth)

    apps[auth["application_token"]] = {
        "BOT_ID": bot_id,
        "COMMANDS": commands,
        "LANGUAGE_ID": lang,
        "AUTH": auth
    }
    save_config(apps)
    return {"status": "ok", "bot_id": bot_id, "commands": commands}