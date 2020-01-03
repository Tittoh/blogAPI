""" This is a test file for the login feature. """
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from ..models import User
from .utils import TEST_USER

class TestLogin(APITestCase):
    """ Tests the view function for login. """

    def register_user(self, user):
        """ Register User. """
        self.client.post(
            reverse("authentication:registration"),
            user,
            format='json')

    def test_user_can_login(self):
        """ Tests that a registered user can login. """
        self.register_user(TEST_USER)
        response = self.client.post(
            reverse("authentication:login"), TEST_USER, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Ensure user exist.
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().email, TEST_USER['user']['email'])

    def test_user_logging_in_exists(self):
        """ Tests that a non-existing user cannot login. """
        response = self.client.post(
            reverse("authentication:login"), TEST_USER, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_email_password_required(self):
        """ Tests that email and password are both required for login. """
        response = self.client.post(
            reverse("authentication:login"), format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_email_required(self):
        """ Tests that email is required for login. """
        user = {
            "user": {
                "password": "testpassword"
            }
        }
        response = self.client.post(
            reverse("authentication:login"), user, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_required(self):
        """ Tests that password is required for login. """
        user = {
            "user": {
                "password": "",
                "email": "testemail@mail.com"
            }
        }
        response = self.client.post(
            reverse("authentication:login"), user, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_is_active(self):
        """ Tests that the user logging in us not a banned user. """
        self.register_user(TEST_USER)
        user = User.objects.get()
        user.is_active = False
        user.save()
        response = self.client.post(
            reverse("authentication:login"), TEST_USER, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)