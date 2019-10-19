from hashlib import md5
from clinic_django.settings import apikey as server_side_apikey
from datetime import datetime


def verify_apikey(apikey: str, username: str) -> bool:
    _a = md5()
    _time = str(datetime.now().timestamp())[:9]
    _a.update((server_side_apikey+username+_time).encode())
    return _a.hexdigest() == apikey
