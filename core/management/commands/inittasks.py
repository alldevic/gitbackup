from django.core.management.base import BaseCommand
from django_q.models import Schedule
from django.core.exceptions import ObjectDoesNotExist


class Command(BaseCommand):
    help = 'Инициализация тасок'

    def handle(self, *args, **options):
        # Create backup task
        try:
            Schedule.objects.get(name='getbackup')
        except ObjectDoesNotExist:
            self.stdout.write(self.style.SUCCESS('Create getbackup'))
            Schedule.objects.create(
                name='getbackup',
                func='django.core.management.call_command',
                args='"getbackup"',
                schedule_type=Schedule.MINUTES,
                minutes=5
            )
