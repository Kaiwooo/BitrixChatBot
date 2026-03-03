import logging
from fastapi import FastAPI
from webhooks import install, event, bot_unreg, bot_reg, bot_list

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI()
app.include_router(install.router, prefix="/install")
app.include_router(event.router, prefix="/event")
app.include_router(bot_unreg.router, prefix="/botunreg")
app.include_router(bot_reg.router, prefix="/botreg")
app.include_router(bot_list.router, prefix="/botlist")