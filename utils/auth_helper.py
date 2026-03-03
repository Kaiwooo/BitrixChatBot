def extract_auth(data: dict):
    """
    Извлекает auth[...] параметры из входящего запроса Bitrix
    и возвращает словарь вида:
    {
        "access_token": "...",
        "refresh_token": "...",
        ...
    }
    """
    return {
        k[5:-1]: v
        for k, v in data.items()
        if k.startswith("auth[") and k.endswith("]")
    }