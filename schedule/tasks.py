from datetime import datetime, timedelta
from celery import shared_task
from .models import Duration, Mark

@shared_task
def delete_old_schedule():
    from .models import Lesson
    life = Duration.objects.get('Lesson').duration
    objects = Lesson.objects
    exp = datetime.now() - timedelta(minutes=life)
    objects.filter(created__lte=exp).delete()

@shared_task
def delete_old_mark():
    from .models import Lesson
    life = Duration.objects.get('Mark').duration
    objects = Mark.objects
    exp = datetime.now() - timedelta(minutes=life)
    objects.filter(created__lte=exp).delete()