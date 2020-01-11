""" Test update and view profile """
import json
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.test import APIClient

from django.urls import reverse
from django.contrib.auth import get_user_model

TEST_USER = {
    "user": {
        "email": "test@mail.com",
        "password": "Pass123.",
        "username": "testuser"
    }
}


class TestUserProfile(APITestCase):
    """ Test all the jwt funtions """

    client = APIClient()

    def register_user(self, user):
        """
        Register User and returns a user response
        having blank bio and image fields.
        """
        response = self.client.post(
            reverse("authentication:registration"),
            user,
            format='json')
        response.render()
        user = json.loads(response.content)
        return user

    def test_get_profile(self):
        """
        This displays the initial user profile after registration
        """
        user_details = self.register_user(TEST_USER).get("user")
        token = user_details['token']
        name = user_details['username']

        url = reverse("profiles:view_profile", args=[name])
        self.client.credentials(HTTP_AUTHORIZATION='Bearer '+token)
        response = self.client.get(url)
        response.render()
        profile = json.loads(response.content)
        details = profile["profile"]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(details["bio"], "")

    def test_non_existent_user(self):
        """
        Checking for response when a non user checks his profile
        """
        wrong_name = "my_name"
        url = reverse("profiles:view_profile", args=[wrong_name])
        token = self.register_user(TEST_USER).get("user").get("token")
        self.client.credentials(HTTP_AUTHORIZATION='Bearer '+token)
        response = self.client.get(url)
        response.render()
        profile = json.loads(response.content)
        details = profile["profile"]

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(details["detail"],
                         "The requested profile does not exist.")

    def test_update_profile(self):
        """
        Update user details
        """
        token = self.register_user(TEST_USER).get("user").get("token")
        self.register_user(TEST_USER)

        user = {
            "user": {
                "username": "testuser2",
                "email": "jake@jake.jake2",
                "bio": "My bio",
                "image": "https://static.productionready.io/images/smiley-cyrus.png"
            }
        }

        self.client.credentials(HTTP_AUTHORIZATION='Bearer '+token)
        response = self.client.put(
            reverse("authentication:user"),
            user,
            format="json")

        profile = json.loads(response.content)
        details = profile["user"]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(details["bio"], "My bio")
        