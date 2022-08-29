import dramatiq
from app.models import MailingCampaign, Message

from backend.settings import STAT_RECIPIENTS


def start_scheduled_campaigns() -> None:
    campaigns = MailingCampaign.objects.filter(status=MailingCampaign.Status.SCHEDULED)

    for campaign in campaigns:
        if campaign.ready_to_start:
            campaign.start()


def end_expired_campaigns() -> None:
    campaigns = MailingCampaign.objects.filter(status=MailingCampaign.Status.RUNNING)

    for campaign in campaigns:
        if campaign.has_expired:
            campaign.end()


def send_campaign_report() -> None:
    MailingCampaign.objects.send_stats_to_email(STAT_RECIPIENTS)


@dramatiq.actor(max_retries=0)
def send_message(message_id: int) -> None:
    message = Message.objects.get(id=message_id)
    message.send()


def route_messages(*statuses) -> None:
    messages = Message.objects.filter(status__in=statuses)
    for message in messages:
        send_message.send(message.id)


@dramatiq.actor(max_retries=0)
def route_pending_messages() -> None:
    route_messages(
        Message.Status.ENQUEUED, Message.Status.DELAYED, Message.Status.FAILED
    )
