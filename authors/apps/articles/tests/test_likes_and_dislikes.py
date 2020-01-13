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
        user = User.objects.get()
        article = Article.objects.create(
            title="How to train your dragon",
            description="Ever wonder how?",
            body="You have to believe",
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

    def test_auth_user_can_like(self):
        user = self.create_a_user()
        self.verify_user(user)
        auth_user = self.login_user()
        user = User.objects.get()
        article = self.create_article()

        res = self.client.put('/api/articles/'+article.slug+'/like/',
                              HTTP_AUTHORIZATION='Bearer ' +
                              auth_user['user']['token'],
                              format='json'
                              )
        self.assertEquals(res.status_code, 200)

    def test_auth_user_can_dislike(self):
        user = self.create_a_user()
        self.verify_user(user)
        auth_user = self.login_user()
        user = User.objects.get()
        article = self.create_article()

        res = self.client.put('/api/articles/'+article.slug+'/dislike/',
                              HTTP_AUTHORIZATION='Bearer ' +
                              auth_user['user']['token'],
                              format='json'
                              )
        self.assertEquals(res.status_code, 200)

    def test_like_404_article(self):
        user = self.create_a_user()
        self.verify_user(user)
        auth_user = self.login_user()
        user = User.objects.get()
        slug = 'fake-slug-13qedffd23'

        res = self.client.put('/api/articles/'+slug+'/like/',
                              HTTP_AUTHORIZATION='Bearer ' +
                              auth_user['user']['token'],
                              format='json'
                              )
        self.assertEquals(res.status_code, 404)

    def test_dislike_404_article(self):
        user = self.create_a_user()
        self.verify_user(user)
        auth_user = self.login_user()
        user = User.objects.get()
        slug = 'fake-slug-13qedffd23'

        res = self.client.put('/api/articles/'+slug+'/dislike/',
                              HTTP_AUTHORIZATION='Bearer ' +
                              auth_user['user']['token'],
                              format='json'
                              )
        self.assertEquals(res.status_code, 404)

    def test_like_disliked_article(self):
        user = self.create_a_user()
        self.verify_user(user)
        auth_user = self.login_user()
        user = User.objects.get()
        article = self.create_article()

        self.client.put('/api/articles/'+article.slug+'/dislike/',
                        HTTP_AUTHORIZATION='Bearer ' +
                        auth_user['user']['token'],
                        format='json'
                        )

        res = self.client.put('/api/articles/'+article.slug+'/like/',
                              HTTP_AUTHORIZATION='Bearer ' +
                              auth_user['user']['token'],
                              format='json'
                              )

        self.assertEquals(res.status_code, 200)

    def test_dislike_liked_article(self):
        user = self.create_a_user()
        self.verify_user(user)
        auth_user = self.login_user()
        user = User.objects.get()
        article = self.create_article()

        self.client.put('/api/articles/'+article.slug+'/like/',
                        HTTP_AUTHORIZATION='Bearer ' +
                        auth_user['user']['token'],
                        format='json'
                        )

        res = self.client.put('/api/articles/'+article.slug+'/dislike/',
                              HTTP_AUTHORIZATION='Bearer ' +
                              auth_user['user']['token'],
                              format='json'
                              )

        self.assertEquals(res.status_code, 200)
