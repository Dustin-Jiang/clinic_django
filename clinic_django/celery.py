from __future__ import absolute_import #, unicode_literals
import os
from celery import Celery
from django.utils import timezone

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clinic_django.settings')

app = Celery('clinic_django')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# 解决时区问题,定时任务启动就循环输出
# app.now = timezone.now()

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()