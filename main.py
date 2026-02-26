from fastapi import FastAPI
from webhooks import install, event

app = FastAPI()
app.include_router(install.router, prefix="/install")
app.include_router(event.router, prefix="/event")