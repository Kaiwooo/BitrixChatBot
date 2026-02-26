# client.py
import aiohttp
from storage import save_config, load_config
from config import CLIENT_ID, CLIENT_SECRET, DEBUG
import logging

async def call(method: str, params: dict, auth: dict):
    url = f"{auth['client_endpoint']}{method}"
    params["auth"] = auth["access_token"]

    # 🔥 ЛОГИРУЕМ РЕАЛЬНЫЙ REST ЗАПРОС

    payload = params.copy()
    payload["auth"] = auth["access_token"]

    logging.info("========== BITRIX REST REQUEST ==========")
    logging.info(f"URL: {url}")
    logging.info(f"METHOD: POST")
    logging.info(f"PAYLOAD: {payload}")
    logging.info("=========================================")

    if DEBUG:
        print("REST CALL:", url, params)
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=params) as resp:
            result = await resp.json()
            status = resp.status
            text = await resp.text()

        # 🔥 ЛОГИРУЕМ ОТВЕТ
    logging.info("========== BITRIX REST RESPONSE ==========")
    logging.info(f"STATUS: {status}")
    logging.info(f"BODY: {text}")
    logging.info("==========================================")




    if "error" in result and result["error"] in ("expired_token", "invalid_token"):
        auth = await refresh_token(auth)
        if auth:
            return await call(method, params, auth)
    return result

async def refresh_token(auth: dict):
    if not CLIENT_ID or not CLIENT_SECRET or "refresh_token" not in auth:
        return None
    url = "https://oauth.bitrix.info/oauth/token/"
    params = {
        "grant_type": "refresh_token",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": auth["refresh_token"]
    }
    if DEBUG:
        print("REFRESH TOKEN:", url, params)
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=params) as resp:
            result = await resp.json()
    if "error" not in result:
        cfg = load_config()
        app_token = auth.get("application_token")
        if app_token:
            cfg[app_token]["AUTH"] = result
            save_config(cfg)
        return result
    return None