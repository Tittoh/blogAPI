from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from authors.apps.core.utils import random_string_generator, generate_slug
from authors.apps.core.models import TimeModel

from authors.apps.authentication.models import User
from authors.apps.profiles.models import Profile

class Article(TimeModel):
    """ This class represents the Article model """
    slug = models.SlugField(db_index=True, max_length=255, unique=True)
    title = models.CharField(db_index=True, max_length=255)
    description = models.TextField()
    body = models.TextField()
    author = models.ForeignKey(
                    'profiles.Profile',
                    on_delete=models.CASCADE,
                    related_name='articles')
    # default image for the article.
    image_url = models.URLField(blank=True, null=True)
    likes = models.ManyToManyField(User, related_name="likes", blank=True)
    dislikes = models.ManyToManyField(
        User, related_name="dislikes", blank=True)
    tags = models.ManyToManyField('articles.Tag', related_name='articles')

    def __str__(self):
        return self.title

@receiver(pre_save, sender=Article)
def add_slug_to_article_if_not_exists(sender, instance, *args, **kwargs):
    """ create a signal to add slug field if None exists. """
    slug = generate_slug(instance.title)
    if instance and not instance.slug:
        instance.slug = slug
        return

    article = Article.objects.get(slug = instance.slug)
    if article.title != instance.title:
        instance.slug = slug
        return

class Comment(TimeModel):
    """ Model to represent a Comment. """
    body = models.TextField()

    article = models.ForeignKey(
        'articles.Article', related_name='comments', on_delete=models.CASCADE
    )

    author = models.ForeignKey(
        'profiles.Profile', related_name='comments', on_delete=models.CASCADE
    )

    parent = models.ForeignKey(
        'self', null=True, blank=False, on_delete=models.CASCADE, related_name='thread'
    )

class Rate(models.Model):
    """Ratings model."""
    ratings = models.IntegerField(null=False)
    counter = models.IntegerField(default=0)
    article = models.ForeignKey(Article, on_delete=models.CASCADE,
            related_name="rate")
    rater = models.ForeignKey(Profile, on_delete=models.CASCADE)

@receiver(pre_save, sender=Rate)
def add_one_to_counter(sender, instance, *args, **kwargs):
    """ create a signal to add counter value by one. """

    instance.counter = instance.counter + 1

class Tag(TimeModel):
    """
    Tags model
    """
    tag = models.CharField(max_length=255)
    slug = models.SlugField(db_index=True, unique=True)

    def __str__(self):
        return '{}'.format(self.tag)
