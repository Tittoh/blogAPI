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

class FilterTestCase(APITestCase):
    """Test Cases to test ratings feature"""

    def setUp(self):
        """Initialize default data."""
        self.user = {
                "user":{
                    "username":"test",
                    "email":"info@test.co",
                    "password":"Test123."
                    }
                }
        self.author = {
                "user":{
                    "username":"author",
                    "email":"info@author.co",
                    "password":"Test123."
                    }
                }
        self.article1 = {
            "article": {
                "title": "How to train your dragon",
                "description": "Ever wonder how?",
                "body": "You have to believe",
                "tagList": ["django-rest", "python"]
            }
        }

    def login_user(self, user):
        """
        login user in order to access jwt token
        """
        response = self.client.post(
            reverse("authentication:login"),
            user,
            format='json')
        response.render()
        user = json.loads(response.content)
        return user

    def create_a_user(self, username, email,
            password):
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
        user = User.objects.filter(username="author").first()
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

    def test_can_filter_by_title(self):
        """ Tests that a user can filter articles by title """
        author = self.create_a_user("author", "info@author.co", "Test123.")
        self.verify_user(author) # Verify created author
        # Login test user and return authorization token.
        auth_author = self.login_user(self.author) 
        article = self.create_article() # create article
        res = self.client.get('/api/articles?title=django',
                                    format='json'
                                    )
        response = json.loads(res.content)
        self.assertEquals(response['results'][0]['title'], "django")
        self.assertEquals(res.status_code, 200)

    def test_filter_by_title_non_existence_title(self):
        """ Tests thae results with non existence title. """
        author = self.create_a_user("author", "info@author.co", "Test123.")
        self.verify_user(author) # Verify created author
        # Login test user and return authorization token.
        auth_author = self.login_user(self.author) 
        article = self.create_article() # create article
        res = self.client.get('/api/articles?title=random',
                                    format='json'
                                    )
        response = json.loads(res.content)
        self.assertEquals(len(response['results']), 0)

    def test_filter_by_author(self):
        """ Tests that can filter by author. """
        author = self.create_a_user("author", "info@author.co", "Test123.")
        self.verify_user(author) # Verify created author
        # Login test user and return authorization token.
        auth_author = self.login_user(self.author) 
        article = self.create_article() # create article
        res = self.client.get('/api/articles?author__id=20',
                                    format='json'
                                    )
        response = json.loads(res.content)
        self.assertEquals(response['results'][0]['title'], "django")

    def test_filter_by_non_existence_author(self):
        """ Tests thae results with non existence author. """
        author = self.create_a_user("author", "info@author.co", "Test123.")
        self.verify_user(author) # Verify created author
        # Login test user and return authorization token.
        auth_author = self.login_user(self.author) 
        article = self.create_article() # create article
        res = self.client.get('/api/articles?author__id=6',
                                    format='json'
                                    )
        response = json.loads(res.content)
        self.assertEquals(response['results'], [])

    def test_filter_by_tag(self):
        """ Tests that can filter by tags. """
        author = self.create_a_user("author", "info@author.co", "Test123.")
        self.verify_user(author) # Verify created author
        # Login test user and return authorization token.
        auth_author = self.login_user(self.author) 
        article = self.create_article() # create article
        self.client.post('/api/articles/',
                                    self.article1,
                                    HTTP_AUTHORIZATION='Bearer ' +
                                    auth_author['user']['token'],
                                    format='json'
                                    )
        res = self.client.get('/api/articles?tags__tag=python',
                                    format='json'
                                    )
        response = json.loads(res.content)
        self.assertEquals(response['results'][0]['title'], "How to train your dragon")

    def test_filter_by_non_existent_tag(self):
        """ Tests filter with non existing tags. """
        author = self.create_a_user("author", "info@author.co", "Test123.")
        self.verify_user(author) # Verify created author
        # Login test user and return authorization token.
        auth_author = self.login_user(self.author) 
        article = self.create_article() # create article
        self.client.post('/api/articles/',
                                    self.article1,
                                    HTTP_AUTHORIZATION='Bearer ' +
                                    auth_author['user']['token'],
                                    format='json'
                                    )
        res = self.client.get('/api/articles?tags__tag=random',
                                    format='json'
                                    )
        response = json.loads(res.content)
        self.assertEquals(response['results'], [])
