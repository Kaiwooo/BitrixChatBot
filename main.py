import logging
from fastapi import FastAPI
from webhooks import install, event, unregister_bot, register_bot

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

app = FastAPI()
app.include_router(install.router, prefix="/install")
app.include_router(event.router, prefix="/event")
app.include_router(unregister_bot.router, prefix="/unregister")
app.include_router(register_bot.router, prefix="/register")