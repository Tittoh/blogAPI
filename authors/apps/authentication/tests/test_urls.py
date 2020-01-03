""" Test urls. """
from django.test import TestCase
from django.urls import reverse, resolve


class TestUrls(TestCase):
    """ Test that URLs exist. """

    def test_registration_url(self):
        """ Tests if url for registration exists. """
        url = reverse("authentication:registration")
        self.assertEqual(resolve(url).view_name, "authentication:registration")

    def test_login_url(self):
        """ Tests if url for login exists. """
        url = reverse("authentication:login")
        self.assertEqual(resolve(url).view_name, "authentication:login")

    def test_user_retreive_update_url(self):
        """ Tests if url for updating user exists. """
        url = reverse("authentication:update_user")
        self.assertEqual(resolve(url).view_name, "authentication:update_user")
