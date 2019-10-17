from rest_framework import permissions
from clinic_django.settings import apikey

class ApikeyPermission(permissions.BasePermission):
    # whether has X-API-KEY or is_staff are ok to go
    def has_permission(self, request, view):
        if request.headers.get('X-API-KEY') == apikey:
            return True

        if request.user.is_staff:
            return True

    def has_object_permission(self, request, view, obj):
        if request.headers.get('X-API-KEY') == apikey:
            return True
        if request.user.is_staff:
            return True


class ClinicUserPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_staff:
            return True
        elif view.action != 'list':
            return True
        else:
            return False

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        elif request.user == obj:
            return True
        else:
            return False
