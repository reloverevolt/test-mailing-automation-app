from app.models import MobileOperator
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class ClientTests(APITestCase):
    def setUp(self):
        self.url = reverse("client-create")
        self.accurate_create_data = {
            "phone": "79998887766",
            "operator": "Beeline",
            "timezone": "UTC",
            "tag": "test tag",
        }
        call_command("load_timezones")
        MobileOperator.objects.create(
            name=self.accurate_create_data["operator"], prefix=961
        )

    def test_create_client_201(self):
        response = self.client.post(self.url, self.accurate_create_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_client_500_bad_phone(self):
        bad_phone_cases = ["89998887766", "+79998887766", "799988877665"]
        for phone in bad_phone_cases:
            modified_data = self.accurate_create_data
            modified_data["phone"] = phone
            response = self.client.post(
                self.url, self.accurate_create_data, format="json"
            )

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(
                response.json()["phone"],
                ["Not valid phone format. Please use 7XXXXXXXXXX"],
            )

    def test_create_client_400_bad_operator(self):
        modified_data = self.accurate_create_data
        modified_data["operator"] = "Megafon"
        response = self.client.post(self.url, self.accurate_create_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json()["operator"],
            [f'Operator {modified_data["operator"]} is not supported'],
        )

    def test_create_client_400_bad_timezone(self):
        modified_data = self.accurate_create_data
        modified_data["timezone"] = "Random Timezone"
        response = self.client.post(self.url, self.accurate_create_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json()["timezone"],
            [f'Timezone {modified_data["timezone"]} is not supported'],
        )
