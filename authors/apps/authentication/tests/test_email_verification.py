""" This is a test file for the login feature. """
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from ..models import User
from .utils import TEST_USER
from django.core import mail
from ..views import VerifyAccount
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from ..utils import generate_token
from rest_framework.test import force_authenticate
from rest_framework.test import APIRequestFactory


class TestLogin(APITestCase):
    """ Tests the view function for login. """

    def register_user(self, user):
        """ Register User. """
        self.client.post(
            reverse("authentication:registration"),
            user,
            format='json')

    def test_send_email(self):
        """ Tests that a verification email is sent on signup """
        self.register_user(TEST_USER)

        # Test that one message has been sent.
        self.assertEqual(len(mail.outbox), 1)

        # Verify that the subject of the first message is correct.
        self.assertEqual(mail.outbox[0].subject, 'Verify your account')

    def test_account_has_been_verified(self):
        """ Tests that the account is verified """
        self.register_user(TEST_USER)
        user = User.objects.get()
        token = generate_token.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        request = APIRequestFactory().get(
            reverse("authentication:verify", args=[uid, token]))
        verify_account = VerifyAccount.as_view()
        response = verify_account(request, uidb64=uid, token=token)
        self.assertTrue(response.status_code, 200)
        user = User.objects.get()

        # Verify that the account has been verified
        self.assertTrue(user.is_confirmed)

    def test_invalid_verification_link(self):
        """ Tests an invalid token """
        self.register_user(TEST_USER)
        user = User.objects.get()
        token = generate_token.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(9))
        request = APIRequestFactory().get(
            reverse("authentication:verify", args=[uid, token]))
        verify_account = VerifyAccount.as_view()
        response = verify_account(request, uidb64=uid, token=token)
        self.assertTrue(response.status_code, 200)
        user = User.objects.get()

        # Verify that the account has not been verified
        self.assertFalse(user.is_confirmed)
