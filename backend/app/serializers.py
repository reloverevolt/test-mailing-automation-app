import re

from app.models import Client, MailingCampaign, MobileOperator, Tag, Timezone
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers


class OperatorField(serializers.RelatedField):
    def to_representation(self, value):
        return value.name

    def to_internal_value(self, data):
        try:
            operator = MobileOperator.objects.get(name=data)
        except ObjectDoesNotExist:
            raise serializers.ValidationError(f"Operator {data} is not supported")

        return operator


class TagField(serializers.RelatedField):
    def to_representation(self, value):
        return value.name

    def to_internal_value(self, data):
        tag, created = Tag.objects.get_or_create(name=data)
        return tag


class TimezoneField(serializers.RelatedField):
    def to_representation(self, value):
        return value.name

    def to_internal_value(self, data):
        try:
            timezone = Timezone.objects.get(name=data)
        except ObjectDoesNotExist:
            raise serializers.ValidationError(f"Timezone {data} is not supported")

        return timezone


class ClientDetailSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    phone = serializers.CharField()
    operator = OperatorField(queryset=MobileOperator.objects.all())
    timezone = TimezoneField(queryset=Timezone.objects.all())
    tag = TagField(queryset=Tag.objects.all())

    class Meta:
        model = Client
        fields = "__all__"

    def validate_phone(self, value):
        if not re.search(r"^7\d{10}$", value):
            raise serializers.ValidationError(
                "Not valid phone format. Please use 7XXXXXXXXXX"
            )

        return value


class MailingCampaignDetailSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    status = serializers.CharField(read_only=True)
    tag = TagField(many=True, queryset=Tag.objects.all())
    operator = OperatorField(many=True, queryset=MobileOperator.objects.all())

    class Meta:
        model = MailingCampaign
        fields = "__all__"
