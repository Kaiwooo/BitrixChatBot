import logging
from b24pysdk import BitrixToken, Client
from config import DEBUG

# кэш клиентов по application_token
b24_clients = {}

def get_b24(auth: dict):
    """
    Возвращает объект Bitrix SDK для конкретного auth.
    """
    app_token = auth.get("application_token")
    if not app_token:
        raise ValueError("Auth должен содержать application_token")

    if app_token not in b24_clients:
        token = BitrixToken(
            auth_token=auth["access_token"],
            refresh_token=auth.get("refresh_token"),
            domain=auth.get("client_endpoint")  # либо auth.get("domain")
        )
        b24_clients[app_token] = Client(token, prefer_version=3)

    return b24_clients[app_token]


async def call(method: str, params: dict, auth: dict):
    b24 = get_b24(auth)
    if DEBUG:
        print("SDK CALL:", method, params)
    try:
        response = await b24.call(method, params)
        return response.result  # SDK возвращает объект с .result
    except Exception as e:
        logging.error(f"❌ Ошибка SDK вызова {method}: {e}")
        raise