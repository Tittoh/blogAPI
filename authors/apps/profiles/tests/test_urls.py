from django.test import TestCase
from django.urls import reverse, resolve


class TestProfileUrls(TestCase):
    ''' Tests that URLs for profiles app exist. '''

    def test_get_user_profile_url(self):
        ''' Test if url for retrieving user profile exists. '''
        url = reverse("profiles:view_profile", args=['username'])

        self.assertEqual(resolve(url).view_name, "profiles:view_profile")

    def test_follow_user_url(self):
        ''' Test if url for following user profile exists. '''
        url = reverse("profiles:follow_profile",
                      args=['username'])

        self.assertEqual(resolve(url).view_name, "profiles:follow_profile")
