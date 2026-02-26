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
    content_type = request.headers.get("content-type", "")

    if "application/json" in content_type:
        data = await request.json()
    else:
        form = await request.form()
        data = dict(form)

        import json
        if "data" in data:
            data["data"] = json.loads(data["data"])

    logger.info(f"EVENT DATA: {data}")

    return {"result": "ok"}