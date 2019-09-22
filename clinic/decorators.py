'''
@Date: 2019-08-12 18:22:23
@LastEditTime: 2019-08-12 18:28:29
@Description: file content
@Author: Tang Yuming
@LastEditors: Feng Kaiyu
'''
from django.http import HttpResponseForbidden, HttpResponseRedirect, HttpRequest
from django.urls import reverse
from functools import wraps
from clinic_django.settings import apikey


def login_require(func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse('cas_ng_login'))
        else:
            return func(request, *args, **kwargs)
    return wrapper


def worker_require(func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse('cas_ng_login'))
        elif not (request.user.is_staff and request.user.is_superuser):
            return HttpResponseForbidden()
        else:
            return func(request, *args, **kwargs)
    return wrapper


def cas_only(func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse('cas_ng_login'))
        else:
            return func(request, *args, **kwargs)
    return wrapper


def with_apikey(func):
    @wraps(func)
    def wrapper(request: HttpRequest, *args, **kwargs):
        if not request.headers.get('apikey') == apikey:
            return HttpResponseForbidden("bad apikey")
        else:
            return func(request, *args, **kwargs)
    return wrapper
