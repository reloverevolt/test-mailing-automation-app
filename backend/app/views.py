from app.models import Client, MailingCampaign
from app.serializers import ClientDetailSerializer, MailingCampaignDetailSerializer
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response


class ClientDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ClientDetailSerializer
    queryset = Client.objects.all()

    def perform_update(self, serializer):
        validated_data = serializer.validated_data
        serializer.save(**validated_data)


class ClientCreateView(generics.CreateAPIView):
    serializer_class = ClientDetailSerializer
    queryset = Client.objects.all()

    def perform_create(self, serializer):
        validated_data = serializer.validated_data
        serializer.save(**validated_data)


class StatsViewSet(viewsets.ViewSet):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "campaign_ids",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(type=openapi.TYPE_STRING),
                required=False,
            )
        ],
        responses={
            200: openapi.Response(
                description="Sample campaign stats report",
                examples={"application/json": MailingCampaign.objects.get_stats()},
            )
        },
    )
    @action(detail=False, methods=["get"])
    def mailing_campaign_report(self, request):
        campaign_ids = request.query_params.get("campaign_ids")
        if campaign_ids:
            campaign_ids = campaign_ids.split(",")

        report = MailingCampaign.objects.get_stats(campaign_ids)

        return Response(report, status=status.HTTP_200_OK)


class MailingCampaignDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = MailingCampaignDetailSerializer
    queryset = MailingCampaign.objects.all()

    def perform_update(self, serializer):
        validated_data = serializer.validated_data
        serializer.save(**validated_data)


class MailingCampaignCreateView(generics.CreateAPIView):
    serializer_class = MailingCampaignDetailSerializer
    queryset = MailingCampaign.objects.all()

    def perform_create(self, serializer):
        validated_data = serializer.validated_data
        serializer.save(**validated_data)
