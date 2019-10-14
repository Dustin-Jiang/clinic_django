from django.contrib import admin
# from django.contrib.auth.admin import UserAdmin
from .models import ClinicUser, Record, Date, Announcement, Campus

# Register your models here.
@admin.register(Record)
class RecordAdmin(admin.ModelAdmin):
    list_display = ('user', 'real_name', 'worker', 'status')

@admin.register(ClinicUser)
class ClinicUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'realname', 'is_staff', 'campus', 'school')
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