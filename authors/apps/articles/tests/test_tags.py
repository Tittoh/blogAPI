import json
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from authors.apps.authentication.models import User
from authors.apps.authentication.tests.utils import TEST_USER
from django.core import mail
from authors.apps.authentication.views import VerifyAccount
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from authors.apps.authentication.utils import generate_token
from rest_framework.test import force_authenticate
from rest_framework.test import APIRequestFactory
from authors.apps.articles.models import Article

user = {
    "user": {
        "username": "test",
        "email": "info@test.co",
        "password": "Test123."
    }
}

class TestTags(APITestCase):
    """
    This class defines the test suite for the tags of an article.
    """

    def setUp(self):
        """Define the test client and other test variables."""

        self.article1 = {
            "article": {
                "title": "How to train your dragon",
                "description": "Ever wonder how?",
                "body": "You have to believe",
                "tagList": ["django-rest", "python"]
            }
        }
        self.bad_tag_list = {
            "article": {
                "title": "How to train your dragon",
                "description": "Ever wonder how?",
                "body": "You have to believe",
                "tagList": "django-rest, python"
            }
        }
        self.tag_tuple = {
            "article": {
                "title": "How to train your dragon",
                "description": "Ever wonder how?",
                "body": "You have to believe",
                "tagList": ("django-rest, python")
            }
        }
        self.user = {
             "user": {
                 "username": "test",
                 "email": "info@test.co",
                 "password": "Test123."
             }
         }

    def login_user(self, user=user):
        """
        login user
        """
        response = self.client.post(
            reverse("authentication:login"),
            user,
            format='json')
        response.render()
        user = json.loads(response.content)
        return user

    def create_a_user(self, username='test', email='info@test.co',
                      password='Test123.'):
        """
        Create a test user
        """
        user = User.objects.create_user(username, email, password)
        user.save()
        return user

    def create_article(self):
        """
        Create a test article
        """
        tags = ["django-rest", "python"]
        user = User.objects.get()
        article = Article.objects.create(
            title="How to train your dragon",
            description="Ever wonder how?",
            body="You have to believe",
            tagList=tags,
            author=user.profile)
        article.save()
        return article

    def verify_user(self, user):
        """Verify user"""
        token = generate_token.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        request = APIRequestFactory().get(
            reverse("authentication:verify", args=[uid, token]))
        verify_account = VerifyAccount.as_view()
        verify_account(request, uidb64=uid, token=token)
        return user

    #Test cases
    def test_tagList_added(self):
        """Test a tagList is added when an article is created"""
        user = self.create_a_user()
        self.verify_user(user)
        auth_user = self.login_user()
        user = User.objects.get()
        response = self.client.post('/api/articles/',
                                    self.article1,
                                    HTTP_AUTHORIZATION='Bearer ' +
                                    auth_user['user']['token'],
                                    format='json'
                                    )
        self.assertIn("django-rest", response.content.decode()),
        self.assertIn("python", response.content.decode())

    def test_tagList_returned(self):
        """Test api can return a taglist with an article"""
        user = self.create_a_user()
        self.verify_user(user)
        auth_user = self.login_user()
        self.client.post('/api/articles/',
                                    self.article1,
                                    HTTP_AUTHORIZATION='Bearer ' +
                                    auth_user['user']['token'],
                                    format='json'
                                    )
        response = self.client.get('/api/articles/',
                                    format='json'
                                    )
        self.assertIn("django-rest", response.content.decode()),
        self.assertIn("python", response.content.decode())

    def test_get_tagList(self):
        """
        Test api can get a tagList
        """

        user = self.create_a_user()
        self.verify_user(user)
        auth_user = self.login_user()
        self.client.post('/api/articles/',
                         self.article1,
                         HTTP_AUTHORIZATION='Bearer ' +
                         auth_user['user']['token'],
                         format='json'
                         )
        response = self.client.get('/api/tags/',
                                   format='json'
                                   )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_tagList_object(self):
        """
        Test a tagList cannot be a string
        """

        user = self.create_a_user()
        self.verify_user(user)
        auth_user = self.login_user()
        response = self.client.post('/api/articles/',
                         self.bad_tag_list,
                         HTTP_AUTHORIZATION='Bearer ' +
                         auth_user['user']['token'],
                         format='json'
                         )
        self.assertNotIn("django-rest", response.content.decode()),
        self.assertNotIn("python", response.content.decode())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_tagList_data_structure(self):
        """
        Test a tagList cannot be a tuple
        """

        user = self.create_a_user()
        self.verify_user(user)
        auth_user = self.login_user()
        response = self.client.post('/api/articles/',
                         self.tag_tuple,
                         HTTP_AUTHORIZATION='Bearer ' +
                         auth_user['user']['token'],
                         format='json'
                         )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
