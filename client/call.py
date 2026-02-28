import aiohttp
from config import DEBUG
from refresh_token import refresh_token

async def call(method: str, params: dict, auth: dict):
    url = f"{auth['client_endpoint']}{method}"
    params["auth"] = auth["access_token"]

    if DEBUG:
        print("REST CALL:", url, params)
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=params) as resp:
            result = await resp.json()
    if "error" in result and result["error"] in ("expired_token", "invalid_token"):
        auth = await refresh_token(auth)
        if auth:
            return await call(method, params, auth)
    return result