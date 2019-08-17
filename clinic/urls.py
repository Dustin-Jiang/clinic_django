from django.urls import path, include
from .views import manage
from .views import ClinicUserViewSet, RecordViewSet, RecordViewSetWechat, DateViewSet
from rest_framework import routers
from .views4serializer import ClinicUserView

router = routers.DefaultRouter()
router.register('users', ClinicUserViewSet, 'clinicuser')
router.register('records', RecordViewSet, 'record')
router.register('wechat', RecordViewSetWechat, 'wechat')
router.register('date', DateViewSet, 'date')


urlpatterns = [
    path('manage/', manage, name="manage_index"),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api/user/', ClinicUserView.as_view()),
    path('api/', include(router.urls)),
]
