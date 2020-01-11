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

    def login_user(self):
        """
        login user
        """
        response = self.client.post(
            reverse("authentication:login"),
            self.user,
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


    def test_user_can_create_an_article(self):
        """
        Tests that a user can create an article
        """
        user = self.create_a_user()
        self.verify_user(user)
        auth_user = self.login_user()
        user = User.objects.get()
        res = self.client.post('/api/articles/',
                               self.article1,
                                HTTP_AUTHORIZATION='Bearer ' +
                                auth_user['user']['token'],
                                format='json'
                                )
        self.assertEquals(res.status_code, 201)

    def test_unreregistered_user_cannot_create_an_article(self):
        """
        Tests that an unregistered user cannot user cannot create an article
        """
        user = self.create_a_user()
        auth_user = self.login_user()
        user = User.objects.get()
        res = self.client.post('/api/articles/',
                               self.article1,
                               format='json'
                               )
        self.assertEquals(res.status_code, 403)

    def test_create_article_without_title(self):
        """
        Tests an article must have a title
        """
        user = self.create_a_user()
        self.verify_user(user)
        auth_user = self.login_user()
        user = User.objects.get()
        article = {
            "article": {
                "description": "Ever wonder how?",
                "body": "You have to believe",
            }
        }
        res = self.client.post('/api/articles/',
                               article,
                               HTTP_AUTHORIZATION='Bearer ' +
                               auth_user['user']['token'],
                               format='json'
                               )
        self.assertEquals(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_article_without_body(self):
        """
        Tests an article must have a body
        """
        user = self.create_a_user()
        self.verify_user(user)
        auth_user = self.login_user()
        user = User.objects.get()
        article = {
            "article": {
                "title": "how to train your dragon",
                "description": "Ever wonder how?",
            }
        }
        res = self.client.post('/api/articles/',
                               article,
                               HTTP_AUTHORIZATION='Bearer ' +
                               auth_user['user']['token'],
                               format='json'
                               )
        self.assertEquals(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_article_without_description(self):
        """
        Tests an article must have a description
        """
        user = self.create_a_user()
        self.verify_user(user)
        auth_user = self.login_user()
        user = User.objects.get()
        article = {
            "article": {
                "title": "Ever wonder how?",
                "body": "You have to believe",
            }
        }
        res = self.client.post('/api/articles/',
                               article,
                               HTTP_AUTHORIZATION='Bearer ' +
                               auth_user['user']['token'],
                               format='json'
                               )
        self.assertEquals(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_article_with_empty_title(self):
        """
        Tests an article with empty title
        """
        user = self.create_a_user()
        self.verify_user(user)
        auth_user = self.login_user()
        user = User.objects.get()
        article = {
            "article": {
                "title": "",
                "description": "Ever wonder how?",
                "body": "You have to believe",
            }
        }
        res = self.client.post('/api/articles/',
                               article,
                               HTTP_AUTHORIZATION='Bearer ' +
                               auth_user['user']['token'],
                               format='json'
                               )
        self.assertEquals(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_article_with_empty_description(self):
        """
        Tests an article with empty description
        """
        user = self.create_a_user()
        self.verify_user(user)
        auth_user = self.login_user()
        user = User.objects.get()
        article = {
            "article": {
                "title": "test title",
                "description": "",
                "body": "You have to believe",
            }
        }
        res = self.client.post('/api/articles/',
                               article,
                               HTTP_AUTHORIZATION='Bearer ' +
                               auth_user['user']['token'],
                               format='json'
                               )
        self.assertEquals(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_article_with_empty_body(self):
        """
        Tests an article with empty body
        """
        user = self.create_a_user()
        self.verify_user(user)
        auth_user = self.login_user()
        user = User.objects.get()
        article = {
            "article": {
                "title": "test title",
                "description": "You have to believe",
                "body": "",
            }
        }
        res = self.client.post('/api/articles/',
                               article,
                               HTTP_AUTHORIZATION='Bearer ' +
                               auth_user['user']['token'],
                               format='json'
                               )
        self.assertEquals(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_can_get_articles(self):
        """
        Tests that a user can get articles
        """
        user = self.create_a_user()
        self.verify_user(user)
        auth_user = self.login_user()
        user = User.objects.get()
        self.create_article()
        res = self.client.get('/api/articles/',
                               HTTP_AUTHORIZATION='Bearer ' +
                               auth_user['user']['token'],
                               format='json'
                               )
        self.assertEquals(res.status_code, 200)

    def test_user_can_delete_an_article(self):
        """
        Tests that a user can delete a request
        """
        user = self.create_a_user()
        self.verify_user(user)
        auth_user = self.login_user()
        user = User.objects.get()
        article = self.create_article()
        res = self.client.delete('/api/articles/'+article.slug+'/',
                                 HTTP_AUTHORIZATION='Bearer ' +
                                 auth_user['user']['token'],
                                 format='json'
                                 )
        self.assertEquals(res.status_code, 204)

    def test_unauthorised_user_cannot_delete_an_article(self):
        """
        Tests that unauthorised user cannot delete a request
        """
        user = self.create_a_user()
        self.verify_user(user)
        auth_user = self.login_user()
        user = User.objects.get()
        article = self.create_article()
        res = self.client.delete('/api/articles/'+article.slug+'/',
                              format='json'
                              )
        self.assertEquals(res.status_code, 403)

    def test_user_can_update_an_article(self):
        """
        Tests that a user can update an article
        """
        user = self.create_a_user()
        self.verify_user(user)
        auth_user = self.login_user()
        user = User.objects.get()
        article = self.create_article()
        res = self.client.put('/api/articles/'+article.slug+'/',
                               self.article1,
                               HTTP_AUTHORIZATION='Bearer ' +
                               auth_user['user']['token'],
                               format='json'
                               )
        self.assertEquals(res.status_code, 200)

    def test_unauthorised_user_cannot_update_article(self):
        """
        Tests that unauthorised user cannot update an article
        """
        user = self.create_a_user()
        self.verify_user(user)
        auth_user = self.login_user()
        user = User.objects.get()
        article = self.create_article()
        res = self.client.put('/api/articles/'+article.slug+'/',
                              self.article1,
                              format='json'
                              )
        self.assertEquals(res.status_code, 403)

    def test_user_can_get_articles_without_login(self):
        """
        Tests that user can get articles without login
        """
        user = self.create_a_user()
        self.verify_user(user)
        auth_user = self.login_user()
        user = User.objects.get()
        self.create_article()
        res = self.client.get('/api/articles/',
                              format='json'
                              )
        self.assertEquals(res.status_code, 200)

    def test_user_can_get_article_without_login(self):
        """
        Tests that user can get an article without login
        """
        user = self.create_a_user()
        self.verify_user(user)
        auth_user = self.login_user()
        user = User.objects.get()
        article = self.create_article()
        res = self.client.get('/api/articles/'+article.slug+'/',
                              format='json'
                              )
        self.assertEquals(res.status_code, 200)
