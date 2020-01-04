""" Test jwt """
import json
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.test import APIClient

from django.urls import reverse
from django.contrib.auth import get_user_model

from .utils import TEST_USER

class TestJWT(APITestCase):
    """ Test all the jwt funtions """
    def register_user(self, user):
        """ Register User and returns a user response. """
        response = self.client.post(
            reverse("authentication:registration"),
            user,
            format='json')
        response.render()
        user = json.loads(response.content)
        return user

    def test_token_present(self):
        """ Test token must be present """
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ')
        response = client.get(
            reverse("authentication:user")
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_white_space(self):
        """ Test that token cant have white spaces. """
        token = self.register_user(TEST_USER).get("user").get("token")
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + token.replace(".", " "))
        response = client.get(
            reverse("authentication:user")
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_prefix_bearer(self):
        """ Test that token must have bearer as prefix. """
        token = self.register_user(TEST_USER).get("user").get("token")
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='NotBearer ' + token)
        response = client.get(
            reverse("authentication:user")
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_invalid_token(self):
        """ Test token must be valid """
        token = self.register_user(TEST_USER).get("user").get("token")
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + token + "other")
        response = client.get(
            reverse("authentication:user")
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


    def test_deleted_user(self):
        """ Test user must must exist for token to be valid """

        token = self.register_user(TEST_USER).get("user").get("token")
        get_user_model().objects.get().delete()
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        response = client.get(
            reverse("authentication:user")
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


    def test_inactive_user(self):
        """ Test that incative user token does not work. """
        token = self.register_user(TEST_USER).get("user").get("token")

        user = get_user_model().objects.get()
        user.is_active = False
        user.save()

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        response = client.get(
            reverse("authentication:user")
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        