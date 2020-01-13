import json
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.test import APIClient

from django.urls import reverse
from django.contrib.auth import get_user_model
from .test_models import CreateArticle
from authors.apps.articles.models import Article

TEST_USER = {
    "user": {
        "email": "test@mail.com",
        "password": "Pass123.",
        "username": "testuser"
    }
}


class TestFavoriteArticle(APITestCase):
    """ Test all the favorite funtions """

    client = APIClient()

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

    def test_user_favorite_non_existent_article(self):
        """
        Check if user can favorite an article with a non-existent slug.
        """
        user_details = self.register_user(TEST_USER).get("user")
        token = user_details['token']
        name = 'wrong slug :-('

        url = reverse("articles:favorite", args=[name])

        self.client.credentials(HTTP_AUTHORIZATION='Bearer '+token)

        response = self.client.post(url)
        response.render()
        favorite = json.loads(response.content)
        details = favorite["favorite"]["detail"]


        self.assertEquals(details, "An article with this slug does not exist")
        self.assertEquals(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_favorite_article(self):
        article = CreateArticle().create_article()

        user_details = self.register_user(TEST_USER).get("user")
        token = user_details['token']
        slug = article.slug

        url = reverse("articles:favorite", args=[slug])

        self.client.credentials(HTTP_AUTHORIZATION='Bearer '+token)

        response = self.client.post(url)
        response.render()
        favorite = json.loads(response.content)
        count = favorite['favorite']['favoriteCount']
        is_favorited = favorite['favorite']['favorited']

        self.assertEquals(count, 1)
        self.assertEquals(is_favorited, True)
    
    def test_user_unfavorite_non_existent_article(self):
        """
        Check if user can favorite an article with a non-existent slug.
        """
        user_details = self.register_user(TEST_USER).get("user")
        token = user_details['token']
        name = 'wrong slug :-('

        url = reverse("articles:favorite", args=[name])

        self.client.credentials(HTTP_AUTHORIZATION='Bearer '+token)

        response = self.client.delete(url)
        response.render()
        favorite = json.loads(response.content)
        details = favorite["favorite"]["detail"]

        self.assertEquals(details, "An article with this slug does not exist")
        self.assertEquals(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_unfavorite_article(self):
        article = CreateArticle().create_article()

        user_details = self.register_user(TEST_USER).get("user")
        token = user_details['token']
        slug = article.slug

        url = reverse("articles:favorite", args=[slug])

        self.client.credentials(HTTP_AUTHORIZATION='Bearer '+token)

        response = self.client.delete(url)
        response.render()
        favorite = json.loads(response.content)
        count = favorite['favorite']['favoriteCount']

        is_favorited = favorite['favorite']['favorited']

        self.assertEquals(count, 0)
        self.assertEquals(is_favorited, False)
