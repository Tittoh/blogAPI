""" utils provide data and methods used for testing. """
from django.contrib.auth import get_user_model
from authors.apps.authentication.models import User
from authors.apps.articles.models import Article

TEST_USER = {
    "user": {
        "email": "test@mail.com",
        "password": "Pass123.",
        "username": "testuser"
    }
}

def create_article():
    """
    Create a test article
    """
    user = User.objects.get()
    article = Article.objects.create(
                title="django",
                description="django tests",
                body="body", author=user.profile)
    article.save()
    return article


def create_user(username="testuser", email="testuser@mail.com",
                password="Pass123."):
    """ create_user() creates and returns a user. """
    user = get_user_model().objects.create_user(username, email, password=password)
    user.save()
    return user
