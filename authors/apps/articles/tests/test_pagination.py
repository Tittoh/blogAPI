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


class ArticleCRUDTestCase(APITestCase):
    """Test Cases to test ratings feature"""

    def setUp(self):
        """Initialize default data."""

        self.user = {
            "user": {
                "username": "test",
                "email": "info@test.co",
                "password": "Test123."
            }
        }
        self.user1 = {
            "user": {
                "username": "Jacob",
                "email": "jake@jake.com",
                "password": "Test123."
            }
        }
        self.article1 = {
            "article": {
                "title": "How to train your dragon",
                "description": "Ever wonder how?",
                "body": "You have to believe",
            }
        }

        self.article2 = {
            "article": {
                "title": "How to feed your dragon",
                "description": "Wanna know how?",
                "body": "You don't believe?",
            }
        }

    def login_user(self, user=user):
        """
        Login user
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
        user = User.objects.get()
        article = Article.objects.create(
            title="How to train your dragon",
            description="Ever wonder how?",
            body="You have to believe",
            author=user.profile)
        article.save()
        return article

    def verify_user(self, user):
        """ Verify user """
        token = generate_token.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        request = APIRequestFactory().get(
            reverse("authentication:verify", args=[uid, token]))
        verify_account = VerifyAccount.as_view()
        verify_account(request, uidb64=uid, token=token)
        return user

    def test_pagination_returns_9_articles(self):
        """
        Tests that pagination only returns 12 articles per page.
        """
        user = self.create_a_user()
        self.verify_user(user)
        auth_user = self.login_user()
        user = User.objects.get()
        for article in range(20):
            self.client.post('/api/articles/',
                             self.article1,
                             HTTP_AUTHORIZATION='Bearer ' +
                             auth_user['user']['token'],
                             format='json'
                             )
        res = self.client.get('/api/articles/', format='json')
        results = len(json.loads(res.content).get('article').get('results'))
        self.assertEquals(res.status_code, 200)
        self.assertEquals(results, 12)
