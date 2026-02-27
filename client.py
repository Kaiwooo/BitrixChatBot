from b24pysdk import BitrixToken, BitrixApp
from config import DEBUG

b24_clients = {}  # кэш по application_token

def get_b24(auth: dict):
    """
    Возвращает объект Bitrix SDK для конкретного auth.
    """
    app_token = auth.get("application_token")
    if not app_token:
        raise ValueError("Auth должен содержать application_token")

    if app_token not in b24_clients:
        token = BitrixToken(
            access_token=auth.get("access_token"),
            refresh_token=auth.get("refresh_token"),
            application_token=app_token
        )
        b24_clients[app_token] = BitrixApp(token, api_version="v3")
    return b24_clients[app_token]

# client.py
async def call(method: str, params: dict, auth: dict):
    b24 = get_b24(auth)
    # SDK возвращает Python dict сразу
    if DEBUG:
        print("SDK CALL:", method, params)
    try:
        result = await b24.call(method, params)
        return result
    except Exception as e:
        print(f"❌ Ошибка вызова {method}: {e}")
        raise