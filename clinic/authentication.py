from clinic_django.settings import apikey
from .models import ClinicUser
from rest_framework import authentication
from rest_framework import exceptions
from .utils import verify_apikey
import logging
# Get an instance of a logger
logger = logging.getLogger('django')

class ApikeyAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):

        logger.info('`X-Forwarded-For` is %s' % request.headers.get('X-Forwarded-For'))
        logger.info('HOST is %s' % request.get_host())
        # 这里可以增加识别 HOSTNAME 的操作 `request.get_host()`
        # 不过目前似乎没有太大必要
        _apikey = request.headers.get('X-API-KEY')
        if not _apikey:
            return None
        username = request.query_params.get('username')
        if not username:
            return None
        _datetime = request.headers.get('Date')
        # verify hash
        if not verify_apikey(_apikey, username, _datetime):
            return None
            
        try:
            user = ClinicUser.objects.get(username=username)
        except ClinicUser.DoesNotExist:
            user = ClinicUser(username=username)
            user.save()
            return (user, None)
            # raise exceptions.AuthenticationFailed('No such user')
        return (user, None)