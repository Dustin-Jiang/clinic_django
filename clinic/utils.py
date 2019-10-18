from hashlib import md5
from clinic_django.settings import apikey as server_side_apikey


def verify_apikey(apikey: str, username: str) -> bool:
    _a = md5()
    _a.update((server_side_apikey+username).encode())
    return _a.hexdigest() == apikey
