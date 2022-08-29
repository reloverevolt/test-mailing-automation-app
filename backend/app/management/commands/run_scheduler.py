import pytz
from app.tasks import (
    end_expired_campaigns,
    route_pending_messages,
    send_campaign_report,
    start_scheduled_campaigns,
)
from apscheduler.schedulers.background import BlockingScheduler
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Run blocking scheduler to create periodical tasks"

    def handle(self, *args, **options) -> None:
        self.stdout.write(self.style.NOTICE("Preparing scheduler"))
        scheduler = BlockingScheduler(timezone=pytz.UTC)
        scheduler.add_job(start_scheduled_campaigns, "interval", seconds=60)
        scheduler.add_job(end_expired_campaigns, "interval", seconds=60)
        scheduler.add_job(route_pending_messages.send, "interval", seconds=60)
        scheduler.add_job(send_campaign_report, "interval", hours=24)
        self.stdout.write(self.style.NOTICE("Starting scheduler"))
        scheduler.start()
