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
from .models import FINISHED_STATUS, WORKING_STATUS, ClinicUser, Date, Record, Campus
from .permissions import ApikeyPermission, ClinicUserPermission
from .serializers import (ClinicUserSerializer, DateSerializer,
                          RecordSerializer, RecordSerializerWechat, CampusSerializer)
# Create your views here.

weekday_list = ['work_mon', 'work_tue', 'work_wedn', 'work_thu',
                            'work_fri', 'work_sat', 'work_sun']


class RecordViewSetWechat(viewsets.ModelViewSet):
    permission_classes = (ApikeyPermission,)
    authentication_classes = (ApikeyAuthentication,)
    serializer_class = RecordSerializerWechat

    def get_queryset(self):
        username = self.request.query_params['username']
        # 现在 list 只会得到已有的工单
        return Record.objects.filter(user__username=username).exclude(status__in=WORKING_STATUS,
                                                                      appointment_time__lt=datetime.now())

    @action(detail=False, methods=["GET"])
    def finish(self, request):
        queryset = self.filter_queryset(
            self.get_queryset()).filter(status__in=FINISHED_STATUS)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
        

    # def list(self, request, *args, **kwargs):
    #     queryset = self.filter_queryset(
    #         self.get_queryset()).filter(status__in=FINISHED_STATUS)

    #     page = self.paginate_queryset(queryset)
    #     if page is not None:
    #         serializer = self.get_serializer(page, many=True)
    #         return self.get_paginated_response(serializer.data)

    #     serializer = self.get_serializer(queryset, many=True)
    #     return Response(serializer.data)

    @action(detail=False, methods=["GET"])
    def working(self, request):
        username = self.request.query_params['username']
        try:
            _record = Record.objects.get(
                user__username=username, status__in=WORKING_STATUS)
            context = {
                "request": request
            }
            serializer = RecordSerializerWechat(_record, context=context)
            ret = {
                'count': 1,
                'data': serializer.data
            }
        except ObjectDoesNotExist:
            ret = {
                'count': 0,
            }
        return Response(ret)

    def perform_create(self, serializer: RecordSerializer):

        # 不在营业时间内的工单不接
        try:
            d = Date.objects.get(
                date=serializer.validated_data['appointment_time'],
                campus__name=serializer.validated_data['campus']
            )
        except ObjectDoesNotExist:
            raise ValidationError(detail={
                'msg': '该日期诊所停止营业'
            })
        if d.capacity <= d.count():
            raise ValidationError(detail={'msg': '该日期已无剩余容量'})
        # 已有1个working中的工单，则不接新的

        working_record_count: int = Record.objects.filter(
            status__in=WORKING_STATUS, user=self.request.user, appointment_time__gte=datetime.now()).count()

        print("[working_record_count]", working_record_count)
        if working_record_count >= 1:
            raise ValidationError(detail={'msg': '您的未完成工单多于一个'})

        if serializer.validated_data['appointment_time'] < datetime.now().date():
            raise ValidationError(detail={'msg': '无法选择过去的时间'})
        # 这里没有限制：不能提交今天已经结束的服务时间的工单，不过鉴于每天会关闭所有未处理的工单
        # ，这个约束不是很要紧

        try:
            CreateModelMixin.perform_create(self, serializer)
        except Exception as e:
            print(e)

    def perform_destroy(self, instance: Record):
        try:
            d = Date.objects.get(
                date=instance.appointment_time,
                campus=instance.campus
            )
        except ObjectDoesNotExist:
            raise ValidationError(detail={
                'msg': '该日期诊所停止营业'
            })
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

            if is_staff == "True":
                if today == "True":
                    kwargs = {'is_staff': is_staff,
                              weekday_list[weekday]: True}
                    queryset = queryset.filter(**kwargs)
                else:
                    queryset = queryset.filter(is_staff=is_staff).order_by(
                        '-' + weekday_list[weekday])
                if campus is not None:
                    queryset = queryset.filter(campus__name=campus)
        return queryset

    @action(detail=False, permission_classes=[AllowAny], methods=["GET"])
    def me(self, request):
        context = {
            "request": request
        }
        serializer = ClinicUserSerializer(request.user, context=context)
        return Response(serializer.data)


class RecordViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdminUser,)
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
            # 因为传入的是name字段
            queryset = queryset.filter(campus__name=campus)
        return queryset

    @action(detail=False, methods=["POST"])
    def insert(self, request):
        context = {'request': request}
        username = request.data['user']
        try:
            user = ClinicUser.objects.get(username=username)
        except:
            user = ClinicUser(username=username)
            user.save()
        finally:
            user_url = ClinicUserSerializer(
                instance=user, context=context).data['url']
            data = request.data
            data['user'] = user_url
            data['status'] = 2
            data['appointment_time'] = datetime.now().date().isoformat()
            serializer = RecordSerializer(data=data)
            if serializer.is_valid():
                record = Record(**serializer.validated_data)
                try:
                    Date.objects.get(
                        campus__name=serializer.validated_data['campus'],
                        date=datetime.now().date()
                    )
                except ObjectDoesNotExist:
                    raise ValidationError(detail={'msg': '今日诊所停业'})
                record.save()
                return Response(RecordSerializer(instance=record, context=context).data)
            else:
                raise ValidationError(detail={'msg': serializer.errors})


class DateViewSet(viewsets.ModelViewSet):
    queryset = Date.objects.filter(date__gte=date.today())
    serializer_class = DateSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, ]
    pagination_class = None

    def get_queryset(self):

        queryset = super().get_queryset().filter(date__gte=date.today())
        if self.request.user.is_authenticated:
            # 后台用户因为已经登录，所以会进入该语句
            return queryset
        # 对于微信端用户，即使是当天的，一旦结束服务了也无法看见
        return queryset.filter(date=date.today(), endTime__gte=datetime.now().time()) | queryset.filter(date__gt=date.today())

    @action(detail=True, permission_classes=[IsAdminUser])
    def cancel_all(self, request, pk=None):
        "将该服务时间所有未完成工单转为`未到诊所`状态"
        _date = self.get_object()
        # 得到所有当天该地区的 queryset
        _queryset = Record.objects.filter(
            appointment_time=_date.date, campus=_date.campus)
        # 过滤，得到其中的未完成的工单
        _queryset = _queryset.filter(status__in=WORKING_STATUS)
        count = _queryset.count()
        # 转换为 `未到诊所` 状态
        _queryset.update(status=9)
        # serializer = RecordSerializer(_queryset, many=True, context={
        #     'request': self.request})

        return Response({'count': count})

    def perform_create(self, serializer: DateSerializer):
        start = serializer.validated_data['date']
        if start < date.today():
            raise ValidationError(detail={'date': '不能早于今天'})
        super().perform_create(serializer)

    def perform_update(self, serializer: DateSerializer):

        start = serializer.validated_data['date']
        old_start = serializer.instance.date

        if serializer.instance.count() > 0 and start != old_start:
            raise ValidationError("已经有工单存在，无法修改")

        if start < date.today():
            raise ValidationError(detail={'start': '不能早于今天'})
        UpdateModelMixin.perform_update(self, serializer)

    def perform_destroy(self, instance: Date):
        if instance.count() > 0:
            raise ValidationError(detail={'msg':
                                          '已经有工单存在，无法删除'})
        DestroyModelMixin.perform_destroy(self, instance)


class AnnouncementViewSet(viewsets.ModelViewSet):
    queryset = Announcement.objects.filter(expireDate__gte=date.today())
    serializer_class = AnnouncementSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, ]
    pagination_class = None

    def get_queryset(self):
        return super().get_queryset().filter(expireDate__gte=date.today())

    @action(detail=False, methods=["GET"])
    def toc(self, request, pk=None):
        """返回TOS"""
        query = Announcement.objects.filter(tag='TOS').first()
        # 优先级排在最前的一条
        print(query)
        if query:
            return JsonResponse({'content': query.content})
        else:
            return JsonResponse({'content': "暂无公告"})


class CampusViewSet(viewsets.ModelViewSet):
    queryset = Campus.objects.all()
    serializer_class = CampusSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, ]
    pagination_class = None
