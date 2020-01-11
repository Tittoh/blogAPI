""" utils provide data and methods used for testing. """
from django.contrib.auth import get_user_model

TEST_USER = {
    "user": {
        "email": "test@mail.com",
        "password": "Pass123.",
        "username": "testuser"
    }
}

def create_user(username="testuser", email="testuser@mail.com",
                password="Pass123."):
    """ create_user() creates and returns a user. """
    user = get_user_model().objects.create_user(username, email, password=password)
    user.save()
    return user
