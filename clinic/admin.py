from django.contrib import admin
# from django.contrib.auth.admin import UserAdmin
from .models import ClinicUser, Record, Date

# Register your models here.
@admin.register(Record)
class RecordAdmin(admin.ModelAdmin):
    list_display = ('user', 'worker', 'status', 'arrive_time')
    fields = ('user', 'worker', 'realname', 'phone_num', 'status', 'is_appointment', 'arrive_time', 'description',
              'worker_description', 'deal_time', 'model', 'method', 'reject_reason', 'password',
              'is_taken')


@admin.register(ClinicUser)
class ClinicUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'realname', 'is_staff', 'campus', 'school')
    fieldsets = (
        ('基本信息', {
            'fields': ('username', 'realname', 'campus', 'school', 'phone_num')
        }),
        ('工作人员信息', {
            'fields': ('is_staff', 'is_superuser',
                       ('work_mon', 'work_tue', 'work_wedn', 'work_thu',
                        'work_sat', 'work_sun'))
        })
    )

admin.register(Date)