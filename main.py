import logging
from fastapi import FastAPI
from webhooks import install, event, unregister

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

app = FastAPI()
app.include_router(install.router, prefix="/install")
app.include_router(event.router, prefix="/event")
app.include_router(unregister.router, prefix="/unregister")