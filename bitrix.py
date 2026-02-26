from b24pysdk import B24
from app.storage import get_auth

def get_b24(domain: str):
    auth = get_auth(domain)
    if not auth:
        raise Exception("Auth not found")

    return B24(
        domain=domain,
        access_token=auth["access_token"],
        refresh_token=auth["refresh_token"],
        client_id=auth["client_id"],
        client_secret=auth["client_secret"],
    )