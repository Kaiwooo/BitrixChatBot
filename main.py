import logging
from fastapi import FastAPI, Request
from b24pysdk import BitrixApp

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

@app.post("/install")
async def install(request: Request):
    data = await request.json()
    logger.info(f"INSTALL DATA: {data}")

    bx = BitrixApp(data)

    # регистрируем бота
    result = await bx.call(
        "imbot.register",
        {
            "TYPE": "B",
            "CODE": "echo_bot_python",
            "EVENT_MESSAGE_ADD": "/event",
            "PROPERTIES": {
                "NAME": "Echo Bot",
                "COLOR": "AQUA",
            },
        },
    )

    logger.info(f"BOT REGISTER RESULT: {result}")

    return {"result": "installed"}


@app.post("/event")
async def event_handler(request: Request):
    data = await request.json()
    logger.info(f"EVENT: {data}")

    if data.get("event") == "ONIMBOTMESSAGEADD":
        message_data = data.get("data", {})
        message_text = message_data.get("MESSAGE")
        dialog_id = message_data.get("DIALOG_ID")

        bx = BitrixApp(data)

        await bx.call(
            "imbot.message.add",
            {
                "DIALOG_ID": dialog_id,
                "MESSAGE": message_text,
            },
        )

    return {"result": "ok"}