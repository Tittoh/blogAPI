""" Module to test all the views in authentication. """
import json
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

access_token = 'EAAObvwrI2u4BAOLCZC3w9DwGtfiunedqH2u9jFbgV43TQrj9SRoLCePX7TA9Oms19ePvUU5OPgmRSsARUoAe8e0wdLvKjeTtTdXQc7HktXYBPnY4zK97JMxaZBcp03ZCMl9ZBNz8jjOE39MFqOymPF7w38z5f7xMZBzNW9xr39M9MRVsoygNQiZAC2CdZCZCMV8RqeaZAgpgcMgZDZD'
class SocialViewTest(APITestCase):
    """ SocialViewTest tests the view functinality for social authentication. """

    def test_provider_required(self):
        """ Test that provider is required """

        token =  {
                "access_token": access_token,
                "provider": ""
            }
        response = self.client.post(
            reverse("authentication:oauth"),
            token,
            format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_access_token_required(self):
        """ Test that token is required """
        token =  {
                "access_token": "",
                "provider": "facebook"
            }
        response = self.client.post(
            reverse("authentication:oauth"),
            token,
            format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    