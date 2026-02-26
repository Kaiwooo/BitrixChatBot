# webhooks/event.py
from fastapi import APIRouter, Request
from client import call
from storage import load_config

router = APIRouter()

@router.post("/")
async def event(request: Request):
    data = await request.json()
    event = data.get("event")
    params = data.get("data", {}).get("PARAMS", {})
    auth = data.get("auth") or {}

    apps = load_config()
    app_token = auth.get("application_token")
    bot_auth = apps.get(app_token, {}).get("AUTH", auth)

    if event == "ONIMBOTMESSAGEADD":
        chat_id = params.get("DIALOG_ID")
        text = params.get("MESSAGE")
        if chat_id and text:
            await call("imbot.message.add", {
                "DIALOG_ID": chat_id,
                "MESSAGE": f"Echo: {text}"
            }, bot_auth)

    elif event == "ONIMCOMMANDADD":
        for command in data["data"].get("COMMAND", []):
            cmd = command.get("COMMAND")
            if cmd == "echo":
                await call("imbot.command.answer", {
                    "COMMAND_ID": command["COMMAND_ID"],
                    "MESSAGE_ID": command["MESSAGE_ID"],
                    "MESSAGE": f"Echo command received: {command.get('COMMAND_PARAMS')}"
                }, bot_auth)
            elif cmd == "help":
                await call("imbot.command.answer", {
                    "COMMAND_ID": command["COMMAND_ID"],
                    "MESSAGE_ID": command["MESSAGE_ID"],
                    "MESSAGE": "Hello! I am EchoBot for Open Lines."
                }, bot_auth)

    elif event == "ONIMBOTJOINCHAT":
        chat_id = params.get("DIALOG_ID")
        if chat_id:
            await call("imbot.message.add", {
                "DIALOG_ID": chat_id,
                "MESSAGE": "Welcome to EchoBot for Open Lines! Type 'help' for commands."
            }, bot_auth)

    elif event == "ONIMBOTDELETE":
        if app_token in apps:
            del apps[app_token]
            save_config(apps)

    return {"status": "ok"}