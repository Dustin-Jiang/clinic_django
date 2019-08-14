from datetime import datetime
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect, HttpResponseBadRequest, JsonResponse
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import BasicAuthentication
from rest_framework import viewsets, status
from .permissions import RecordPermission, ClinicUserPermission, ApikeyPermission
from .decorators import login_require, worker_require, with_apikey
from .models import Record, ClinicUser
from .serializers import ClinicUserSerializer, RecordSerializer, RecordSerializerWechat
from .authentication import ApikeyAuthentication
# Create your views here.


class RecordViewSetWechat(viewsets.ModelViewSet):
    permission_classes = (ApikeyPermission,)
    authentication_classes = (ApikeyAuthentication,)
    serializer_class = RecordSerializerWechat

    def get_queryset(self):
        username = self.request.query_params['username']
        return Record.objects.filter(user__username=username)


@worker_require
def manage(request):
    if request.method == 'GET':
        return render(request, 'manage/index.html')


class ClinicUserViewSet(viewsets.ModelViewSet):
    permission_classes = (ClinicUserPermission, )
    serializer_class = ClinicUserSerializer

    def get_queryset(self):
        queryset = ClinicUser.objects.all()
        is_staff = self.request.query_params.get('is_staff', None)
        today = self.request.query_params.get('today', None)
        campus = self.request.query_params.get('campus')
        if is_staff is not None:
            weekday = datetime.now().weekday()
            weekday_list = ['work_mon', 'work_tue', 'work_wedn', 'work_thu',
                            'work_fri', 'work_sat', 'work_sun']
            if is_staff == "True":
                if today == "True":
                    kwargs = {'is_staff': is_staff,
                              weekday_list[weekday]: True}
                    queryset = queryset.filter(**kwargs)
                else:
                    queryset = queryset.filter(is_staff=is_staff).order_by(
                        '-' + weekday_list[weekday])
                if campus is not None:
                    queryset = queryset.filter(campus=campus)
        return queryset

    @action(detail=False, permission_classes=[AllowAny], methods=["GET"])
    def me(self, request):
        context = {
            "request": request
        }
        serializer = ClinicUserSerializer(request.user, context=context)
        return Response(serializer.data)


class RecordViewSet(viewsets.ModelViewSet):
    permission_classes = (RecordPermission,)
    serializer_class = RecordSerializer

    @action(detail=True, permission_classes=[IsAdminUser])
    def call_user_back(self, request, pk=None):
        record = self.get_object()
        if record.is_taken:
            return Response({'detail': 'already taken'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'detail': 'send success'})

    def get_queryset(self):
        queryset = Record.objects.all()
        campus = self.request.query_params.get('campus', None)
        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)
        elif campus:
            queryset = queryset.filter(campus=campus)
        return queryset

    def create(self, request):
        if not request.user.is_staff:
            if not request.data['status'] in (1, 4):
                return Response({'detail': "not allowed"}, status=status.HTTP_400_BAD_REQUEST)
            if request.data['status'] == 1:
                if Record.objects.filter(user=request.user, status=1):
                    return Response({'detail': "not allowed"}, status=status.HTTP_400_BAD_REQUEST)
            elif request.data['status'] == 4:
                if Record.objects.filter(user=request.user, status=4):
                    return Response({'detail': "too many request"}, status=status.HTTP_400_BAD_REQUEST)
        return super().create(request)
