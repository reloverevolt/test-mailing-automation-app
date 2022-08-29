import logging
import time
from datetime import datetime
from typing import Dict, List, Optional

import pytz
from django.core.mail import send_mail
from django.db import models
from django.db.models import Count

from backend.settings import EMAIL_HOST_USER, local_timezone, mailing_api

logger = logging.getLogger(__name__)


class Timezone(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name

    @property
    def time_now(self) -> datetime.time:
        timezone = pytz.timezone(self.name)
        datetime_now = datetime.now(timezone)
        return datetime_now.time()


class MobileOperator(models.Model):
    name = models.CharField(max_length=16)
    prefix = models.PositiveSmallIntegerField()

    def __str__(self):
        return f"{self.name} ({self.prefix})"


class Tag(models.Model):
    name = models.CharField(max_length=256)

    def __str__(self):
        return self.name


class Client(models.Model):
    phone = models.CharField(max_length=16)
    operator = models.ForeignKey(
        MobileOperator, related_name="clients_by_operator", on_delete=models.CASCADE
    )
    tag = models.ForeignKey(
        Tag,
        related_name="clients_by_tag",
        null=True,
        default=None,
        on_delete=models.CASCADE,
    )
    timezone = models.ForeignKey(
        Timezone, related_name="clients_by_timezone", on_delete=models.CASCADE
    )

    def __str__(self):
        return self.phone


class Message(models.Model):
    class Status(models.TextChoices):
        ENQUEUED = "ENQUEUED"
        DELAYED = "DELAYED"
        SUCCESS = "SUCCESS"
        FAILED = "FAILED"
        EXPIRED = "EXPIRED"

    status = models.CharField(
        max_length=100, choices=Status.choices, default=Status.ENQUEUED
    )
    client = models.ForeignKey(
        Client, related_name="messages_by_client", on_delete=models.CASCADE
    )
    mailing_campaign = models.ForeignKey(
        "MailingCampaign", related_name="messages_by_campaign", on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, default=None)

    def __str__(self):
        return str(self.id)

    @property
    def time_interval_ok(self) -> bool:
        if self.mailing_campaign.is_time_aware:
            client_time_now = self.client.timezone.time_now
            interval_ok = all(
                [
                    client_time_now > self.mailing_campaign.allowed_from_time,
                    client_time_now < self.mailing_campaign.allowed_to_time,
                ]
            )
            return interval_ok

        return True

    def send(self) -> None:

        if self.status == self.Status.SUCCESS:
            return

        if self.mailing_campaign.has_expired:
            self.status = self.Status.EXPIRED
            self.save()
            logger.info(f"message_id: {self.id} has expired")
            return

        if not self.time_interval_ok:
            self.status = self.Status.DELAYED
            self.save()
            logger.info(f"message_id: {self.id} has has been delayed")
            return

        phone_int = int(self.client.phone)
        ok, code = mailing_api.send_message(
            self.id, self.mailing_campaign.text, phone_int
        )

        if not ok:
            self.status = self.Status.FAILED
            self.save()
            logger.info(f"message_id: {self.id} has failed to be sent")
            return

        self.status = self.Status.SUCCESS
        self.sent_at = datetime.now(local_timezone)
        self.save()
        logger.info(f"message_id: {self.id} has expired")


class StatsManager(models.Manager):
    def get_stats(self, campaign_ids: Optional[List] = None) -> Dict:
        campaign_queryset = self.model.objects.prefetch_related(
            "messages_by_campaign"
        ).all()

        if campaign_ids:
            campaign_queryset = campaign_queryset.filter(id__in=campaign_ids)

        campaigns_list = []
        for campaign_obj in campaign_queryset:
            messages = {}
            messages_by_campaign = campaign_obj.messages_by_campaign.all()
            messages["count"] = messages_by_campaign.count()
            statuses = list(
                messages_by_campaign.values("status").annotate(count=Count("status"))
            )
            messages["statuses"] = statuses
            campaign = {"id": campaign_obj.id, "messages": messages}
            campaigns_list.append(campaign)

        report = {
            "campaigns_count": campaign_queryset.count(),
            "campaigns": campaigns_list,
        }

        return report

    def send_stats_to_email(self, recipients_list: List) -> None:
        stats = self.get_stats()
        date_today = time.strftime("%Y-%m-%d")
        subject = f"Mailing Campaign Report {date_today}"
        from_email = EMAIL_HOST_USER

        lines_list = list()

        campaigns_count = stats["campaigns_count"]
        if campaigns_count:
            campaigns_count_text = f"Total Campaigns: {campaigns_count}\n\n"
            lines_list.append(campaigns_count_text)
            for campaign in stats["campaigns"]:
                campaign_title = f'Campaign {campaign["id"]}:\n\n'
                lines_list.append(campaign_title)

                campaign_messages_count = campaign["messages"]["count"]
                messages_count_text = f"Total Messages: {campaign_messages_count}\n"
                lines_list.append(messages_count_text)
                if not campaign_messages_count:
                    continue
                for message in campaign["messages"]["statuses"]:
                    message_status_count_text = (
                        f'{message["status"]}: {message["count"]}\n'
                    )
                    lines_list.append(message_status_count_text)

            text = "".join(lines_list)
            send_mail(subject, text, from_email, recipients_list)
            logger.info(f"{subject} has been sent")


class MailingCampaign(models.Model):
    class Status(models.TextChoices):
        SCHEDULED = "SCHEDULED"
        RUNNING = "RUNNING"
        ENDED = "ENDED"

    status = models.CharField(
        max_length=100, choices=Status.choices, default=Status.SCHEDULED
    )
    tag = models.ManyToManyField(Tag, related_name="campaigns_by_tag", blank=True)
    operator = models.ManyToManyField(
        MobileOperator, related_name="campaigns_by_operator", blank=True
    )
    text = models.TextField()
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    allowed_from_time = models.TimeField(null=True, default=None)
    allowed_to_time = models.TimeField(null=True, default=None)

    objects = StatsManager()

    def __str__(self):
        return str(self.id)

    @property
    def ready_to_start(self) -> bool:
        if self.status == self.Status.RUNNING or self.has_expired:
            return False
        return datetime.now(local_timezone) > self.start_at

    @property
    def has_expired(self) -> bool:
        return datetime.now(local_timezone) > self.end_at

    @property
    def is_time_aware(self) -> bool:
        if self.allowed_from_time and self.allowed_to_time:
            return True
        return False

    def save(self, *args, **kwargs) -> None:
        if self.has_expired:
            self.status = self.Status.ENDED

        super(MailingCampaign, self).save(*args, **kwargs)

    def start(self) -> None:
        self.status = self.Status.RUNNING
        self.save()

        relevant_clients = Client.objects.filter(
            operator__in=list(self.operator.all()), tag__in=list(self.tag.all())
        )

        messages_to_send = [
            Message(mailing_campaign=self, client=client) for client in relevant_clients
        ]

        Message.objects.bulk_create(messages_to_send)
        logger.info(f"campaign_id: {self.id} has started")

    def end(self) -> None:
        self.status = self.Status.ENDED
        self.save()
        logger.info(f"campaign_id: {self.id} has ended")
