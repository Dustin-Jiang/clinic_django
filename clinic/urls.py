from django.urls import include, path
from rest_framework import routers
from .views import (AnnouncementViewSet, ClinicUserViewSet, DateViewSet,
                    RecordViewSet, RecordViewSetWechat, manage, CampusViewSet)
from .views4serializer import ClinicUserView

router = routers.DefaultRouter()
router.register('users', ClinicUserViewSet, 'clinicuser')
router.register('records', RecordViewSet, 'record')
router.register('wechat', RecordViewSetWechat, 'wechat')
router.register('date', DateViewSet, 'date')
router.register('announcement', AnnouncementViewSet, 'announcement')
router.register('campus', CampusViewSet, 'campus')

urlpatterns = [
    path('manage/', manage, name="manage_index"),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api/user/', ClinicUserView.as_view()),
    path('api/', include(router.urls)),
]
