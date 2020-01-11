from django.test import TestCase
from ...authentication.models import User
from rest_framework.test import APITestCase, APIClient
from django.urls import reverse, resolve
import json

from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from ...authentication.utils import generate_token
from rest_framework import status


class TestFollowAPI(APITestCase):
    ''' Tests the followAPI view. '''

    def test_user_can_follow_profile(self):
        ''' Tests that a user can follow another user '''
        # register at least 2 users with profile
        user = User.objects.create_user(
            username="cooluser", password="myCoolP@$$W0rd", email="cooluser@mail.io")
        user1 = User.objects.create_user(
            username="cooluser1", password="myCoolP@$$W0rd", email="cooluser1@mail.io")
        client = APIClient()
        client.force_authenticate(user=user)
        # make the first user follow the second one
        url = reverse("profiles:follow_profile",
                      args=[user1.username])
        response = client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_can_unfollow_profile(self):
        ''' Tests that a user can unfollow another user '''
        # Register at least 2 users with profile
        user = User.objects.create_user(
            username="cooluser", password="myCoolP@$$W0rd",
            email="cooluser@mail.io")
        user1 = User.objects.create_user(
            username="cooluser1", password="myCoolP@$$W0rd",
            email="cooluser1@mail.io")

        # Authenticate users
        client = APIClient()
        client.force_authenticate(user=user)

        # Make the first user follow the second one
        client.post(reverse("profiles:follow_profile",
                            args=[user1.username]))

        # Make the first user unfollow the second user
        response = client.delete(reverse("profiles:follow_profile",
                                         args=[user1.username]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_can_get_all_followers(self):
        ''' Tests can gat a list of all users who follow them '''
        # register at least 2 users with profile
        user = User.objects.create_user(
            username="cooluser", password="myCoolP@$$W0rd", email="cooluser@mail.io")
        client = APIClient()
        client.force_authenticate(user=user)

        # Get a list of all followers of a user
        response = client.get(reverse("profiles:followers",
                                      args=[user.username]))
        self.assertEqual(json.loads(response.content)['profiles'], [])
        self.assertTrue(status.HTTP_200_OK)

    def test_user_can_get_all_following(self):
        ''' Tests can gat a list of all users they follow '''
        # register at least 2 users with profile
        user = User.objects.create_user(
            username="cooluser", password="myCoolP@$$W0rd", email="cooluser@mail.io")
        client = APIClient()
        client.force_authenticate(user=user)

        # Get a list of all followers of a user
        response = client.get(reverse("profiles:following",
                                      args=[user.username]))
        self.assertEqual(json.loads(response.content)['profiles'], [])
        self.assertTrue(status.HTTP_200_OK)

    def test_user_cannot_follow_themselves(self):
        ''' Tests that a user can unfollow another user '''
        # Register at least 2 users with profile
        user = User.objects.create_user(
            username="cooluser", password="myCoolP@$$W0rd",
            email="cooluser@mail.io")

        # Authenticate users
        client = APIClient()
        client.force_authenticate(user=user)

        # Make the first user follow the second one
        response = client.post(reverse("profiles:follow_profile",
                                       args=[user.username]))

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
