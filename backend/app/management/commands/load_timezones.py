import pytz
from app.models import Timezone
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options) -> None:
        if not Timezone.objects.all().exists():
            timezone_list = pytz.all_timezones
            timezone_object_list = [
                Timezone(name=timezone) for timezone in timezone_list
            ]
            Timezone.objects.bulk_create(timezone_object_list)
