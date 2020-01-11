from django.db import models

from authors.apps.core.models import TimeModel
from django.conf import settings


class Profile(TimeModel):
    # There is an inherent relationship between the Profile and
    # User models. By creating a one-to-one relationship between the two, we
    # are formalizing this relationship. Every user will have one -- and only
    # one -- related Profile model.
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )

    # Each user profile will have a field where they can tell other users
    # something about themselves. This field will be empty when the user
    # creates their account, so we specify blank=True.
    bio = models.TextField(blank=True)

    # In addition to the `bio` field, each user may have a profile image or
    # avatar. This field is not required and it may be blank.
    image = models.URLField(blank=True)

    follows = models.ManyToManyField(
        'self', related_name='followed_by', symmetrical=False)
    favorites = models.ManyToManyField(
        'articles.Article', symmetrical=False, related_name='users_favorites')


    def __str__(self):
        return self.user.username

    def follow(self, profile):
        self.follows.add(profile)

    def unfollow(self, profile):
        self.follows.remove(profile)

    def get_followers(self, profile):
        return profile.followed_by.all()

    def get_following(self, profile):
        return profile.follows.all()

    def favorite(self, article):
        self.favorites.add(article)

    def unfavorite(self, article):
        self.favorites.remove(article)
