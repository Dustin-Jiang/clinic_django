from clinic_django.settings import apikey
from .models import ClinicUser
from rest_framework import authentication
from rest_framework import exceptions


class ApikeyAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        if not request.headers.get('X-API-KEY') == apikey:
            return None
        username = request.query_params.get('username')
        if not username:
            return None
            
        try:
            user = ClinicUser.objects.get(username=username)
        except ClinicUser.DoesNotExist:
            user = ClinicUser(username=username)
            user.save()
            return (user, None)
            # raise exceptions.AuthenticationFailed('No such user')

        return (user, None)
