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
    realname = models.CharField('姓名', max_length=50, blank=True, null=True)
    phone_num = models.CharField('电话号码', max_length=50, blank=True, null=True)
    campus = models.CharField('校区', max_length=5, choices=CAMPUS, default="LX")
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
        return "{}-{}".format(self.username, self.realname)


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
    realname = models.CharField('姓名', max_length=50, blank=True, null=True)
    phone_num = models.CharField('电话号码', max_length=50, blank=True, null=True)
    status = models.PositiveSmallIntegerField('状态', default=1, choices=STATUS)
    is_appointment = models.BooleanField('是否预约', blank=True, null=True)
    campus = models.CharField(
        '校区', default="LX", max_length=50, choices=CAMPUS)
    appointment_time = models.DateField('预约日期')
    arrive_time = models.DateTimeField('到达时间', blank=True, null=True)
    description = models.CharField(
        '问题自述', max_length=300)
    worker_description = models.CharField(
        '问题描述', max_length=300, blank=True, null=True)
    deal_time = models.DateTimeField('完成时间', blank=True, null=True)
    model = models.CharField('电脑型号', blank=True, null=True, max_length=30)
    method = models.CharField('处理方法', max_length=300, blank=True, null=True)
    reject_reason = models.CharField(
        '拒绝理由', max_length=300, blank=True, null=True)
    password = models.CharField('密码', max_length=30, blank=True, null=True)
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
    name = models.CharField('名称', default="正常服务", max_length=30)
    start = models.DateField(verbose_name="开始日期", unique=True)
    capacity = models.PositiveIntegerField(verbose_name="可服务人数")
    count = models.PositiveIntegerField(verbose_name="已使用容量", default=0)
    finish = models.PositiveIntegerField(verbose_name="已完成数量", default=0)


class Announcement(models.Model):
    """accouncement related things."""

    TAG_CHOICE = (
        ('AN', '普通公告'),
        ('TOC', '免责声明')
    )

    title = models.CharField('标题', max_length=30)
    content = models.TextField("内容")
    tag = models.CharField("类型", max_length=5, choices=TAG_CHOICE)
    createdTime = models.DateTimeField(
        "创建时间", auto_now=False, auto_now_add=True)
    lastEditedTime = models.DateTimeField(
        "最后编辑时间", auto_now=True, auto_now_add=False)
    expireDate = models.DateField(
        '失效时间'
    )

    def is_available(self):
        return datetime.datetime.now() < self.expireDate
    is_available.short_description = '是否过期'

    def __str__(self):
        return self.title


class Campus(models.Model):
    """campuses of bit""" 

    name = models.CharField('校区名称', max_length=10)
    address = models.CharField('诊所地址', max_length=100)

    def __str__(self):
        return self.name

