from celery import shared_task
from .models import Date, Record
from datetime import datetime
from .models import WORKING_STATUS
import logging
# Get an instance of a logger
logger = logging.getLogger('django')


@shared_task
def auto_cancel_today_unfinished_records():
    date_queryset = Date.objects.filter(date__lte=datetime.now())
    count = 0
    for date_object in date_queryset:
        record_queryset = Record.objects.filter(
            appointment_time=date_object.date,
            campus=date_object.campus,
            status__in=WORKING_STATUS
        )
        count += record_queryset.count()
        # set to `未到诊所`
        record_queryset.update(status=9)
    logger.info(f'清理未到工单{count}个')
    return {"count":count}
