""" Test user views """
import json

from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.test import APIClient

from django.urls import reverse
from .utils import TEST_USER

class TestUserViews(APITestCase):
    """ Test  User views"""
    def register_user(self, user):
        """ Register User and returns a user response. """
        response = self.client.post(
            reverse("authentication:registration"),
            user,
            format='json')
        response.render()
        user = json.loads(response.content)
        return user

    def test_can_get_user(self):
        """ Test that a user can get data when loged in."""
        token = self.register_user(TEST_USER).get("user").get("token")
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        response = client.get(
            reverse("authentication:user")
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_can_update(self):
        """ Test user can update details. """
        token = self.register_user(TEST_USER).get("user").get("token")
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        user = {
            "user":{
                "username":"userchanged"
            }
        }

        response = client.put(
            reverse("authentication:user"),
            user,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        