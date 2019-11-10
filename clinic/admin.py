from django.contrib import admin
# from django.contrib.auth.admin import UserAdmin
from .models import ClinicUser, Record, Date, Announcement, Campus

# Register your models here.
@admin.register(Record)
class RecordAdmin(admin.ModelAdmin):
    list_display = ('user', 'realname', 'campus', 'worker', 'status')
    list_filter = ('status', 'campus',  'worker')

@admin.register(ClinicUser)
class ClinicUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'realname', 'is_staff', 'campus', 'school')
    search_fields = ('username',)
    list_filter = ('is_staff',)
    fieldsets = (
        ('基本信息', {
            'fields': ('username', 'realname', 'campus', 'school', 'phone_num')
        }),
        ('工作人员信息', {
            'fields': ('is_staff', 'is_superuser',
                       ('work_mon', 'work_tue', 'work_wedn', 'work_thu', 'work_fri', 
                        'work_sat', 'work_sun'))
        })
    )

admin.site.register(Date)

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    readonly_fields = ('createdTime', 'lastEditedTime')
    list_display = ('title', 'tag', 'content')

admin.site.register(Campus)

admin.site.site_header = "网协电脑诊所管理"
admin.site.site_title = "网协电脑诊所超管"
admin.site.index_title = "预约系统管理"