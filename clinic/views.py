from .models import Announcement
from .serializers import AnnouncementSerializer
from datetime import date, datetime

from django.core.exceptions import ObjectDoesNotExist
from django.http import (HttpResponse, HttpResponseBadRequest,
                         HttpResponseRedirect, JsonResponse)
from django.shortcuts import render
from rest_framework import status, viewsets
from rest_framework.authentication import BasicAuthentication
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.mixins import (CreateModelMixin, DestroyModelMixin,
                                   UpdateModelMixin)
from rest_framework.permissions import (AllowAny, IsAdminUser, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from .authentication import ApikeyAuthentication
from .decorators import login_require, with_apikey, worker_require
from .models import FINISHED_STATUS, WORKING_STATUS, ClinicUser, Date, Record
from .permissions import (ApikeyPermission, ClinicUserPermission,
                          RecordPermission)
from .serializers import (ClinicUserSerializer, DateSerializer,
                          RecordSerializer, RecordSerializerWechat)

# Create your views here.


class RecordViewSetWechat(viewsets.ModelViewSet):
    permission_classes = (ApikeyPermission,)
    authentication_classes = (ApikeyAuthentication,)
    serializer_class = RecordSerializerWechat

    def get_queryset(self):
        username = self.request.query_params['username']
        return Record.objects.filter(user__username=username)

    def perform_create(self, serializer: RecordSerializer):

        # 已有1个working中的工单，则不接新的
        print("[working_record_count]", self.request.query_params['username'])

        working_record_count: int = Record.objects.filter(
            status__in=WORKING_STATUS, user=self.request.user).count()

        print("[working_record_count]", working_record_count)
        if working_record_count >= 1:
            raise ValidationError("已超出可申请工单数量")

        # 不在营业时间内的工单不接
        try:
            d = Date.objects.get(
                start=serializer.validated_data['appointment_time'])
        except ObjectDoesNotExist:
            raise ValidationError(detail={
                'appointment_time': '该日期诊所停止营业'
            })
        if d.capacity <= d.count:
            raise ValidationError(detail={'detail': '该日期已无剩余容量'})
        d.count += 1
        d.save()
        CreateModelMixin.perform_create(self, serializer)

    def perform_destroy(self, instance: Record):
        try:
            d = Date.objects.get(
                start=instance.appointment_time
            )
        except ObjectDoesNotExist:
            raise ValidationError(detail={
                'appointment_time': '该日期诊所停止营业'
            })
        d.count -= 1
        d.save()
        DestroyModelMixin.perform_destroy(self, instance)


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

    def perform_update(self, serializer: RecordSerializer):
        if serializer.instance.status in WORKING_STATUS and serializer.validated_data['status'] and serializer.validated_data['status'] in FINISHED_STATUS:
            d = Date.objects.get(start=serializer.instance.appointment_time)
            d.count -= 1
            d.finish += 1
        if serializer.instance.status in FINISHED_STATUS and serializer.validated_data['status'] and serializer.validated_data['status'] in WORKING_STATUS:
            d = Date.objects.get(start=serializer.instance.appointment_time)
            d.count += 1
            d.finish -= 1
        UpdateModelMixin.perform_update(self, serializer)


class DateViewSet(viewsets.ModelViewSet):
    queryset = Date.objects.filter(date__gte=date.today())
    serializer_class = DateSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, ]
    pagination_class = None

    def perform_create(self, serializer: DateSerializer):
        start = serializer.validated_data['start']
        if start < date.today():
            raise ValidationError(detail={'start': '不能早于今天'})
        super().perform_create(serializer)

    def perform_update(self, serializer: DateSerializer):

        start = serializer.validated_data['start']
        old_start = serializer.instance.start

        if serializer.instance.count > 0 and start != old_start:
            raise ValidationError("已经有工单存在，无法修改")

        if start < date.today():
            raise ValidationError(detail={'start': 'earlier than today'})
        UpdateModelMixin.perform_update(self, serializer)

    def perform_destroy(self, instance: Date):
        if instance.count > 0:
            raise ValidationError(detail={'msg':
                                          '已经有工单存在，无法删除'})
        DestroyModelMixin.perform_destroy(self, instance)


class AnnouncementViewSet(viewsets.ModelViewSet):
    queryset = Announcement.objects.filter(expireDate__gte=date.today())
    serializer_class = AnnouncementSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, ]
    pagination_class = None

    @action(detail=False, methods=["GET"])
    def toc(self, request, pk=None):
        """返回TOC"""
        query = Announcement.objects.filter(tag='TOC').last()
        print(query)
        if query:
            return JsonResponse({'content': query.content})
        else:
            return JsonResponse({'content': "暂无公告"})
