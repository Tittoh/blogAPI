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
from authors.apps.articles.models import Article, Rate

class RateTestCase(APITestCase):
    """Test Cases to test ratings feature"""

    def setUp(self):
        """Initialize default data."""
        self.rate = {
                "rate":{
                    "rate":2
                    }
                }
        self.rate_string = {
                "rate":{
                    "rate": "j"
                    }
                }
        self.rate_empty = {
                "rate":{
                    "rate": "" 
                    }
                }
        self.rate_range = {
                "rate":{
                    "rate": 6
                    }
                }
        self.user = {
                "user":{
                    "username":"test",
                    "email":"info@test.co",
                    "password":"Test123."
                    }
                }

    def login_user(self):
        """
        login user in order to access jwt token
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
            title="django",
            description="django sucks",
            body="body", author=user.profile)
        article.save()
        return article

    def verify_user(self, user):
        """Verify user"""
        token = generate_token.make_token(user) # Token for user verifications.
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        request = APIRequestFactory().get(
                reverse("authentication:verify", args=[uid, token]))
        verify_account = VerifyAccount.as_view()
        verify_account(request, uidb64=uid, token=token)
        return user

    def test_can_rate_an_articlej(self):
        """ Tests that a user can rate an article """
        user = self.create_a_user() # create user
        self.verify_user(user) # Verify created user
        # Login test user and return authorization token.
        auth_user = self.login_user() 
        user = User.objects.get()
        article = self.create_article() # create article
        res = self.client.post('/api/articles/'+article.slug+'/rate/',
                                    self.rate,
                                    HTTP_AUTHORIZATION='Bearer ' +
                                    auth_user["user"]["token"],
                                    format='json'
                                    )
        self.assertEquals(res.data["response"]["message"][0], "Successfull.")
        self.assertEquals(res.status_code, 201)

    def test_can_not_rate_more_than_3_times(self):
        """ Should only rate for utmost 3 times."""
        user = self.create_a_user() # create user
        self.verify_user(user) # Verify created user
        # Login test user and return authorization token.
        auth_user = self.login_user() 
        user = User.objects.get()
        article = self.create_article() # create article
        # loop to rate article 3 times.
        x = 0 
        while x < 4:
            self.client.post('/api/articles/'+article.slug+'/rate/',
                                    self.rate,
                                    HTTP_AUTHORIZATION='Bearer ' +
                                    auth_user["user"]["token"],
                                    format='json'
                                    )
            x += 1

        res = self.client.post('/api/articles/'+article.slug+'/rate/',
                                    self.rate,
                                    HTTP_AUTHORIZATION='Bearer ' +
                                    auth_user["user"]["token"],
                                    format='json'
                                    )
        self.assertEquals(res.data["errors"]["message"][0], "You are only allowed torate 3 times")
        self.assertEquals(res.status_code, 403)

    def test_rate_should_be_a_number(self):
        """ Should be an integer."""

        user = self.create_a_user() # create user
        self.verify_user(user) # Verify created user
        # Login test user and return authorization token.
        auth_user = self.login_user() 
        user = User.objects.get()
        article = self.create_article() # create article
        res = self.client.post('/api/articles/'+article.slug+'/rate/',
                                    self.rate_string,
                                    HTTP_AUTHORIZATION='Bearer ' +
                                    auth_user["user"]["token"],
                                    format='json'
                                    )
        res.render()
        errors = json.loads(res.content).get('rate')
        error = errors['errors']['rate'][0]
        self.assertEquals(error, "A valid integer is required.")
        self.assertEquals(res.status_code, 400)

    def test_rate_should_be_between_0_and_5(self):
        """ Should be 0, 1, 2, 3, 4, 5."""

        user = self.create_a_user() # create user
        self.verify_user(user) # Verify created user
        # Login test user and return authorization token.
        auth_user = self.login_user() 
        user = User.objects.get()
        article = self.create_article() # create article
        res = self.client.post('/api/articles/'+article.slug+'/rate/',
                                    self.rate_range,
                                    HTTP_AUTHORIZATION='Bearer ' +
                                    auth_user["user"]["token"],
                                    format='json'
                                    )
        res.render()
        errors = json.loads(res.content).get('rate')
        error = errors['errors']['error'][0]
        self.assertEquals(error, "Rate should be from 0 to 5.")
        self.assertEquals(res.status_code, 400)

    def test_rate_should_not_be_an_empty_string(self):
        """ Should not be an empty string."""

        user = self.create_a_user() # create user
        self.verify_user(user) # Verify created user
        # Login test user and return authorization token.
        auth_user = self.login_user() 
        user = User.objects.get()
        article = self.create_article() # create article
        res = self.client.post('/api/articles/'+article.slug+'/rate/',
                                    self.rate_empty,
                                    HTTP_AUTHORIZATION='Bearer ' +
                                    auth_user["user"]["token"],
                                    format='json'
                                    )
        res.render()
        errors = json.loads(res.content).get('rate')
        error = errors['errors']['rate'][0]
        self.assertEquals(error, "A valid integer is required.")
        self.assertEquals(res.status_code, 400)

    def test_cannot_rate_non_existent_article(self):
        """ Should not rate non existing article."""

        user = self.create_a_user() # create user
        self.verify_user(user) # Verify created user
        # Login test user and return authorization token.
        auth_user = self.login_user() 
        user = User.objects.get()
        article = self.create_article() # create article
        res = self.client.post('/api/articles/random/rate/',
                                    self.rate,
                                    HTTP_AUTHORIZATION='Bearer ' +
                                    auth_user["user"]["token"],
                                    format='json'
                                    )
        res.render()
        errors = json.loads(res.content).get('rate')
        error = errors['errors']['message'][0]
        self.assertEquals(error, "Article doesnt exist.")
        self.assertEquals(res.status_code, 404)
