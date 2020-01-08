from rest_framework.test import APITestCase
from django.contrib.auth.tokens import default_token_generator
from .utils import TEST_USER, create_user
from rest_framework import status
from django.urls import reverse


class TestPasswordReset(APITestCase):
    """ Tests the password reset feature. """

    EMAIL = {
        "email": "testuser@mail.com"
    }

    def test_user_can_receive_reset_password_email(self):
        """ Tests that a registered user can receive a reset
        password email. """
        create_user()
        response = self.client.post(
            reverse("authentication:forgot_password"),
            self.EMAIL, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_can_reset_password(self):
        """ Tests if the user can reset(update) their password. """
        user = create_user()
        token = default_token_generator.make_token(user)
        RESET_DATA = {
            "reset_data": {
                "token": token,
                "email": user.email,
                "new_password": "newpassword"
            }
        }
        response = self.client.put(
            reverse("authentication:reset_password"), RESET_DATA, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, "Password Reset Successful")
