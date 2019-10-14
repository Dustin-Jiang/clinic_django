from django.db import models
from django.contrib.auth.models import AbstractUser
import datetime

# Create your models here.
CAMPUS = (
    ('ZGC', "中关村"),
    ('LX', '良乡'),
)


class ClinicUser(AbstractUser):
    """clinic user."""
    realname = models.CharField('真实姓名', max_length=50, blank=True, null=True)
    phone_num = models.CharField('电话号码', max_length=20, blank=True, null=True) # TODO: 其实感觉用处不大
    campus = models.ForeignKey(
        'Campus', on_delete=models.SET_NULL, null=True, blank=True)
    school = models.CharField('学院', max_length=20, blank=True, null=True)

    work_mon = models.BooleanField('周一值班', default=False)
    work_tue = models.BooleanField('周二值班', default=False)
    work_wedn = models.BooleanField('周三值班', default=False)
    work_thu = models.BooleanField('周四值班', default=False)
    work_fri = models.BooleanField('周五值班', default=False)
    work_sat = models.BooleanField('周六值班', default=False)
    work_sun = models.BooleanField('周天值班', default=False)

    def is_teacher(self):
        # TODO
        return False

    def __str__(self):
        return "{}-{}-{}".format(self.campus, self.username, self.realname)


WORKING_STATUS = [0, 1, 2, 4, 5]
FINISHED_STATUS = [3, 6, 7, 8]


class Record(models.Model):
    """record."""
    class Meta:
        ordering = ['-id']
    status_list = ['上单未解决', '预约待确认', '预约已确认', '预约已驳回',
                   '登记待受理', '正在处理', '已解决问题', '建议返厂', '扔给明天']
    STATUS = [(status, commnet) for status, commnet in enumerate(status_list)]
    user = models.ForeignKey(
        ClinicUser, on_delete=models.CASCADE, related_name='record', verbose_name="顾客", blank=True, null=True)
    worker = models.ForeignKey(
        ClinicUser, on_delete=models.CASCADE, blank=True, null=True, related_name='worker', verbose_name="维修人员")
    realname = models.CharField('真实姓名', max_length=50, blank=True, null=True)
    phone_num = models.CharField('电话号码', max_length=20, blank=True, null=True)
    status = models.PositiveSmallIntegerField('状态', default=1, choices=STATUS)
    campus = models.ForeignKey(
        'Campus', verbose_name="校区", related_name="record", on_delete=models.CASCADE)
    appointment_time = models.DateField('预约日期')
    arrive_time = models.DateTimeField('到达时间', blank=True, null=True)
    description = models.CharField(
        '问题自述', max_length=600)
    worker_description = models.CharField(
        '问题描述', max_length=600, blank=True, null=True)
    deal_time = models.DateTimeField('完成时间', blank=True, null=True)
    model = models.CharField('电脑型号', blank=True, null=True, max_length=200)
    method = models.CharField('处理方法', max_length=600, blank=True, null=True)
    reject_reason = models.CharField(
        '拒绝理由', max_length=600, blank=True, null=True)
    password = models.CharField('密码', max_length=256, blank=True, null=True)
    is_taken = models.BooleanField('是否取走', default=False)

    def __str__(self):
        if self.arrive_time:
            time = self.arrive_time.strftime("%Y/%m/%d")
        else:
            time = "还未到诊所"

        if self.is_appointment:
            return "预约-{name}-{status}-{arrive_time}".format(
                name=self.user.realname, status=self.status_list[self.status], arrive_time=time)
        else:
            return "{name}-{status}-{arrive_time}".format(
                name=self.user.realname, status=self.status_list[self.status], arrive_time=time)


class Date(models.Model):
    """business hour."""
    class Meta:
        ordering = ["date"]
    title = models.CharField('名称', default="正常服务", max_length=20)
    date = models.DateField(verbose_name="开始日期")
    capacity = models.PositiveIntegerField(verbose_name="可服务人数")
    campus = models.ForeignKey(
        'Campus', on_delete=models.SET_NULL, blank=True, null=True)
    startTime = models.TimeField(verbose_name='服务开始时间')
    endTime = models.TimeField(verbose_name='服务结束时间')

    def __str__(self):
        return '{}-{}-{}人'.format(self.date, self.campus, self.capacity)

    def count(self):
        return Record.objects.filter(appointment_time=self.date, campus=self.campus).count()

    def finish(self):
        return Record.objects.filter(appointment_time=self.date, status__in=FINISHED_STATUS, campus=self.campus).count()


class Announcement(models.Model):
    """accouncement related things."""

    class Meta:
        ordering = ['priority', '-createdTime']

    TAG_CHOICE = (
        ('AN', '普通公告'),
        ('TOC', '免责声明'),
        ('TA', '置顶公告')
    )

    title = models.CharField('标题', max_length=20)
    content = models.TextField("内容")
    brief = models.TextField("内容概括", blank=True, default='')
    tag = models.CharField("类型", max_length=16, choices=TAG_CHOICE)
    createdTime = models.DateTimeField(
        "创建时间", auto_now=False, auto_now_add=True)
    lastEditedTime = models.DateTimeField(
        "最后编辑时间", auto_now=True, auto_now_add=False)
    expireDate = models.DateField(
        '失效时间'
    )
    priority = models.PositiveIntegerField(
        '显示优先级', default=1
    )

    def is_available(self):
        return datetime.datetime.now() < self.expireDate
    is_available.short_description = '是否过期'

    def __str__(self):
        return self.title


class Campus(models.Model):
    """campuses of bit"""

    name = models.CharField('校区名称', unique=True, max_length=20)
    address = models.CharField('诊所地址', max_length=128)

    def __str__(self):
        return self.name
