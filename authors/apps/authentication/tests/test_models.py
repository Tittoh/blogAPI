""" Module to test all the authentication model. """
from django.test import TestCase
from ..models import User
from .utils import create_user



class UserModelTest(TestCase):
    """
        UserModelTest provides testcase for the user model.
    """

    def test_can_create_user(self):
        """ test_can_create_user() test that the model can create a user. """
        user = create_user(username='testuser')
        user1 = User.objects.filter(username='testuser').first()
        self.assertEqual(user, user1)

    def test_get_short_name(self):
        """ test_get_short_name() returns the username. """
        user = create_user()
        self.assertEqual(user.username, user.get_short_name())

    def test_get_full_name(self):
        """ test_get_full_name() returns the username. """
        user = create_user()
        self.assertEqual(user.username, user.get_full_name)

    def test_str(self):
        """ test_str() tests the string representation of user. """
        user = create_user(email="testuser@mail.com")
        self.assertEqual(str(user), 'testuser@mail.com')

    def test_username_must_be_provided(self):
        """ test_username_must_be_provided(). """
        with self.assertRaises(TypeError):
            User.objects.create_user(email=None, username=None, password=None)

    def test_email_must_be_provided(self):
        """ test_email_must_be_provided(). """
        with self.assertRaises(TypeError):
            User.objects.create_user(email=None, username="testuser", password=None)


    def test_user_can_updated(self):
        """ test_model_can_update() user can be updated. """
        user = create_user()
        user.username = "testupdate"
        user.save()

        user = User.objects.filter(username="testupdate").first()
        self.assertEqual(user.username, "testupdate")

    def test_timestamp_added(self):
        """ test_timestamp_added() The created_at should be added by default. """
        user = create_user()
        self.assertIsNotNone(user.created_at)

    def test_create_superuser(self):
        """ test_create_superuser() Test that user model can create superuser user. """
        user = User.objects.create_superuser(password="password",
                                             email="superuser@mail.com",
                                             username="superuser")
        self.assertTrue(user.is_superuser)

    def test_create_superuser_password(self):
        """ Test test_create_superuser_password() must have password. """
        with self.assertRaises(TypeError):
            User.objects.create_superuser(password=None,
                                          email="superuser@mail.com",
                                          username="superuser")
