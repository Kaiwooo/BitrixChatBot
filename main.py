import logging
from fastapi import FastAPI
from webhooks.install import router as install_router
from webhooks.event import router as event_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

app = FastAPI()
app.include_router(install_router)
app.include_router(event_router)