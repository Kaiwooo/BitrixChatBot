# client/call.py
import httpx
from client.refresh_token import refresh_token
from storage import load_config, save_config
from config import DEBUG

async def call(method: str, params: dict, auth: dict, app_token: str = None):
    """
    Bitrix REST API с авто-обновлением токена.
    :param method: метод REST API, например "imbot.bot.list"
    :param params: параметры запроса
    :param auth: словарь с auth данными
    :param app_token: ключ приложения в конфиге (для сохранения обновленного токена)
    """
    url = f"{auth['client_endpoint']}{method}"
    params["auth"] = auth["access_token"]

    if DEBUG:
        print("REST CALL:", url, params)

    async with httpx.AsyncClient() as client:
        resp = await client.post(url, data=params)
        result = resp.json()

    # Проверка на устаревший или недействительный токен
    if "error" in result and result["error"] in ("expired_token", "invalid_token"):
        if DEBUG:
            print("Token expired, refreshing...")
        new_auth = await refresh_token(auth)
        if new_auth and app_token:
            # Сохраняем обновленный токен в конфиг
            cfg = load_config()
            cfg[app_token] = new_auth
            save_config(cfg)
            auth = new_auth
            params["auth"] = auth["access_token"]
            # Повторяем запрос с новым токеном
            async with httpx.AsyncClient() as client:
                resp = await client.post(url, data=params)
                result = resp.json()
        else:
            if DEBUG:
                print("Token refresh failed or no app_token provided")

    return result