import logging
from fastapi import FastAPI, Request
from b24pysdk import Bitrix

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# временное хранение auth (для MVP)
auth_data = {}

@app.post("/install")
async def install(request: Request):
    data = await request.json()
    logger.info(f"INSTALL DATA: {data}")

    global auth_data
    auth_data = data.get("auth", {})

    bx = Bitrix(auth_data)

    # регистрируем бота
    result = await bx.call(
        "imbot.register",
        {
            "TYPE": "B",
            "CODE": "echo_bot_python",
            "EVENT_MESSAGE_ADD": "/event",
            "PROPERTIES": {
                "NAME": "Echo Bot Python",
                "COLOR": "AQUA",
            }
        }
    )

    logger.info(f"BOT REGISTER RESULT: {result}")

    return {"result": "installed"}


@app.post("/event")
async def event_handler(request: Request):
    data = await request.json()
    logger.info(f"EVENT: {data}")

    event = data.get("event")

    if event == "ONIMBOTMESSAGEADD":
        message_data = data.get("data", {})
        message_text = message_data.get("MESSAGE")
        dialog_id = message_data.get("DIALOG_ID")

        bx = Bitrix(data.get("auth"))

        await bx.call(
            "imbot.message.add",
            {
                "DIALOG_ID": dialog_id,
                "MESSAGE": message_text,
            }
        )

    return {"result": "ok"}