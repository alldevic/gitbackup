from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django_q.models import Schedule
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings


class Command(BaseCommand):
    help = 'Инициализация тасок'

    def handle(self, *args, **options):
        # Create backup task
        try:
            task = Schedule.objects.get(name='getbackup')
            task.next_run = timezone.now()+timedelta(minutes=1)
            if task.minutes != int(settings.MINUTES):
                task.minutes = int(settings.MINUTES)
            task.save()
        except ObjectDoesNotExist:
            self.stdout.write(self.style.SUCCESS('Create getbackup'))
            Schedule.objects.create(
                name='getbackup',
                func='django.core.management.call_command',
                args='"getbackup"',
                schedule_type=Schedule.MINUTES,
                minutes=int(settings.MINUTES),
                next_run=timezone.now()+timedelta(minutes=1)
            )
