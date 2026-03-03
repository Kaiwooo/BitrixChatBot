import logging
from client.call import call
from fastapi import APIRouter, Request
from utils.auth_helper import extract_auth
from utils.logging_helper import log_dict

logger = logging.getLogger(__name__)
router = APIRouter()

async def handler_join_chat(data: dict, auth: dict):
    dialog_id = data.get("data[PARAMS][DIALOG_ID]")
    if not dialog_id:
        return
    welcome = "Привет! Я EchoBot. Напишите что-нибудь, и я повторю это."
    await call("imbot.message.add", {"DIALOG_ID": dialog_id, "MESSAGE": welcome}, auth)

async def handler_message_add(data: dict, auth: dict):
    dialog_id = data.get("data[PARAMS][DIALOG_ID]")
    message_text = data.get("data[PARAMS][MESSAGE]")
    if not dialog_id or not message_text:
        return
    is_connector = data.get("data[USER][IS_CONNECTOR]")
    if is_connector != "Y":
        return
    reply_text = f"Echo: {message_text}"
    await call("imbot.message.add", {"DIALOG_ID": dialog_id, "MESSAGE": reply_text}, auth)

@router.post("")
async def event(request: Request):
    try:
        data = await request.json()
    except Exception:
        form = await request.form()
        data = dict(form)
    log_dict(logger, {"Inbound Event": data})
    auth = extract_auth(data)
    if not auth:
        logger.error("❌ Auth not found")
        return
    event_type = data.get("event")
    logger.info(f"📌 Event type: {event_type}")

    handlers = {
        "ONIMBOTJOINCHAT": handler_join_chat,
        "ONIMBOTMESSAGEADD": handler_message_add,
    }
    handler = handlers.get(event_type)

    if handler:
        await handler(data, auth)
    else:
        log_dict(logger, {"Inbound Event": data})