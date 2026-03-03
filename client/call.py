import httpx
from client.refresh_token import refresh_token
from config import DEBUG

async def call(method: str, params: dict, auth: dict):
    url = f"{auth['client_endpoint']}{method}"
    params["auth"] = auth["access_token"]

    if DEBUG:
        print("REST CALL:", url, params)
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, data=params)
        result = resp.json()
    if "error" in result and result["error"] in ("expired_token", "invalid_token"):
        auth = await refresh_token(auth)
        if auth:
            return await call(method, params, auth)
    return result