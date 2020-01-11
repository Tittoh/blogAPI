from rest_framework.test import APITestCase
from authors.apps.authentication.models import User

from authors.apps.articles.models import Article


class CreateArticle():
    def __init__(self):
        self.title = 'My awesome title'
        self.body = 'this is a test body'
        self.description = 'testing'

    def create_a_user(self, username='fry', email='fry@futur.ama', password='Qwerty!234'):
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
        user = self.create_a_user()
        article = Article.objects.create(
            title=self.title,
            description=self.description,
            body=self.body, author=user.profile)
        article.save()
        return article
