import json
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.test import APIClient

from django.urls import reverse
from authors.apps.articles.models import Article

TEST_USER = {
    "user": {
        "email": "test@mail.com",
        "password": "Pass123.",
        "username": "testuser"
    }
}


class TestSearch(APITestCase):
    """
    Test user search for articles from title, description, body, author
    """

    def setUp(self):
        self.client = APIClient()

        self.article1 = {
            "article": {
                "title": "How to train your dragon",
                "description": "Ever wonder how?",
                "body": "You have to believe",
                "tagList": ["django-rest", "python"]
            }
        }

    def register_user(self, user):
        """
        Register User and returns a user response
        having blank bio and image fields.
        """
        response = self.client.post(
            reverse("authentication:registration"),
            user,
            format='json')
        response.render()
        user = json.loads(response.content)
        return user

    def test_user_search_from_article_title(self):
        """
        Users can get articles when they search for the title's keyword
        """
        token = self.register_user(TEST_USER).get("user").get("token")

        url = "/api/articles/"

        self.client.credentials(HTTP_AUTHORIZATION='Bearer '+token)

        self.client.post(
            url,
            self.article1,
            format='json'
        )

        url = reverse("articles:filter_search") + '?search=How'
        response = self.client.get(url)
        response.render()
        results = json.loads(response.content)
        title = results['results'][0]['title']
        self.assertEquals(title, 'How to train your dragon')
        self.assertIsInstance(results, dict)

    def test_user_search_from_non_existent_article_title(self):
        """
        Users cannot get articles when they search for the wrong title's keyword
        """
        url = reverse("articles:filter_search") + '?search=how'
        response = self.client.get(url)
        response.render()
        results = json.loads(response.content)
        empty = results['count']
        self.assertEquals(empty, 0)
        self.assertIsInstance(results, dict)

    def test_user_search_from_article_body(self):
        """
        Users can get articles when they search for the body's keyword
        """
        token = self.register_user(TEST_USER).get("user").get("token")

        url = "/api/articles/"

        self.client.credentials(HTTP_AUTHORIZATION='Bearer '+token)

        self.client.post(
            url,
            self.article1,
            format='json'
        )

        url = reverse("articles:filter_search") + '?search=believe'
        response = self.client.get(url)
        response.render()
        results = json.loads(response.content)
        body = results['results'][0]['body']
        self.assertEquals(body, 'You have to believe')
        self.assertIsInstance(results, dict)

    def test_user_search_from_non_existent_article_body(self):
        """
        Users cannot get articles when they search for the wrong body's keyword
        """
        url = reverse("articles:filter_search") + '?search=how'
        response = self.client.get(url)
        response.render()
        results = json.loads(response.content)
        empty = results['count']
        self.assertEquals(empty, 0)
        self.assertIsInstance(results, dict)

    def test_user_search_from_article_description(self):
        """
        Users can get articles when they search for the description's keyword
        """
        token = self.register_user(TEST_USER).get("user").get("token")

        url = "/api/articles/"

        self.client.credentials(HTTP_AUTHORIZATION='Bearer '+token)

        self.client.post(
            url,
            self.article1,
            format='json'
        )

        url = reverse("articles:filter_search") + '?search=Ever'
        response = self.client.get(url)
        response.render()
        results = json.loads(response.content)
        description = results['results'][0]['description']
        self.assertEquals(description, 'Ever wonder how?')
        self.assertIsInstance(results, dict)

    def test_user_search_from_non_existent_article_description(self):
        """
        Users cannot get articles when they search for the wrong description's keyword
        """
        url = reverse("articles:filter_search") + '?search=how'
        response = self.client.get(url)
        response.render()
        results = json.loads(response.content)
        empty = results['count']
        self.assertEquals(empty, 0)
        self.assertIsInstance(results, dict)

    def test_user_search_from_article_author(self):
        """
        Users can get articles when they search for the author's keyword
        """
        token = self.register_user(TEST_USER).get("user").get("token")

        url = "/api/articles/"

        self.client.credentials(HTTP_AUTHORIZATION='Bearer '+token)

        self.client.post(
            url,
            self.article1,
            format='json'
        )

        url = reverse("articles:filter_search") + '?search=testuser'
        response = self.client.get(url)
        response.render()
        results = json.loads(response.content)
        author = results['results'][0]['author']['username']
        self.assertEquals(author, 'testuser')
        self.assertIsInstance(results, dict)

    def test_user_search_from_non_existent_article_author(self):
        """
        Users cannot get articles when they search for the wrong author's keyword
        """
        url = reverse("articles:filter_search") + '?search=how'
        response = self.client.get(url)
        response.render()
        results = json.loads(response.content)
        empty = results['count']
        self.assertEquals(empty, 0)
        self.assertIsInstance(results, dict)

    def test_user_search_from_tag(self):
        """
        Users can get articles when they search for the tag's keyword
        """
        token = self.register_user(TEST_USER).get("user").get("token")

        url = "/api/articles/"

        self.client.credentials(HTTP_AUTHORIZATION='Bearer '+token)

        self.client.post(
            url,
            self.article1,
            format='json'
        )
        url = reverse("articles:filter_search") + '?search=python'

        response = self.client.get(url)
        response.render()
        results = json.loads(response.content)
        tag = results['results'][0]['tagList'][0]
        self.assertEquals(tag, 'python')
        self.assertIsInstance(results, dict)

    def test_user_search_from_non_existent_tag(self):
        """
        Users cannot get articles when they search for the wrong tag's keyword
        """
        url = reverse("articles:filter_search") + '?search=how'
        response = self.client.get(url)
        response.render()
        results = json.loads(response.content)
        empty = results['count']
        self.assertEquals(empty, 0)
        self.assertIsInstance(results, dict)
