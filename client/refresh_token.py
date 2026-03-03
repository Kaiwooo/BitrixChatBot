import httpx
from storage import save_config, load_config
from config import CLIENT_ID, CLIENT_SECRET, DEBUG

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
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, json=params)
        result = resp.json()

    if "error" not in result:
        cfg = load_config()
        app_token = auth.get("application_token")
        if app_token:
            cfg[app_token] = result
            save_config(cfg)
        return result
    return None