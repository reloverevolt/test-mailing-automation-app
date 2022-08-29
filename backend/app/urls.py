from app.views import (
    ClientCreateView,
    ClientDetailView,
    MailingCampaignCreateView,
    MailingCampaignDetailView,
    StatsViewSet,
)
from django.urls import path

mailing_stats_overall = StatsViewSet.as_view({"get": "mailing_campaign_report"})

urlpatterns = [
    path("clients/<int:pk>", ClientDetailView.as_view(), name="client-detail"),
    path("clients/create", ClientCreateView.as_view(), name="client-create"),
    path(
        "stats/mailing_campaigns", mailing_stats_overall, name="stats-mailing_campaigns"
    ),
    path(
        "campaigns/<int:pk>",
        MailingCampaignDetailView.as_view(),
        name="campaign-detail",
    ),
    path(
        "campaigns/create", MailingCampaignCreateView.as_view(), name="campaign-create"
    ),
]
