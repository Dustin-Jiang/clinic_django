from hashlib import md5
from clinic_django.settings import apikey as server_side_apikey
from datetime import datetime


def verify_apikey(apikey: str, username: str, time: str) -> bool:
    if not (apikey and username and time):
        return False;
    _a = md5()
    _a.update((server_side_apikey+username+time).encode())
    return _a.hexdigest() == apikey
