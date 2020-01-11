""" module to test comment feature """
import json
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.test import APIClient

from django.urls import reverse
from django.test import TestCase

from authors.apps.articles.models import Comment, Article

from .utils import create_user, create_article


class ModelTestCase(TestCase):
    """ Test the comment model. """
    def test_can_create_comment(self):
        """ should be able to create a comment with model """
        user = create_user()
        article = Article(body="The post", title="Title", description="Cool", author=user.profile)
        article.save()
        comment = Comment(author=user.profile, body="Hello", article=article)
        comment.save()
        new_comment = Comment.objects.get()
        self.assertEqual(comment, new_comment)

    def test_can_create_comment_thread(self):
        """ Should be able to create a comment thread with model. """
        user = create_user()
        article = Article(body="The post", title="Title", description="Cool", author=user.profile)
        article.save()

        comment = Comment(author=user.profile, body="Hello", article=article)
        comment.save()

        comment_reply = Comment(author=user.profile, body="Hello 2.", article=article)
        comment_reply.save()

        comment.thread.add(comment_reply)
        comment = Comment.objects.filter(parent=comment)

        self.assertEqual(len(comment.all()), 1)
        self.assertEqual(comment.all()[0], comment_reply)

    def test_can_get_article_comments(self):
        """  Should be able to get comment for an article using the model. """
        user = create_user()
        article = Article(body="The post", title="Title", description="Cool", author=user.profile)
        article.save()

        comment = Comment(author=user.profile, body="Hello", article=article)
        comment.save()

        comments = article.comments.all()

        self.assertEqual(comment, comments[0])

class CommentViews(APITestCase):
    """ Testcase for the comment view functionlity. """
    def setUp(self):
        """ Initialize default data. """
        self.client = APIClient()

        self.comment = {
            "comment": {
                "body": "His name was my name too."
            }
        }

        self.sub_comment = {
            "comment": {
                "body": "So was i."
            }
        }
        self.user = create_user()
        self.client.force_authenticate(user=self.user)

    def test_can_create_comment(self):
        """ Should be able to create comment via the api """
        article = create_article()
        url = reverse("articles:comments", kwargs={'article_slug':article.slug})
        response = self.client.post(url, self.comment, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_can_create_comment_thread(self):
        """ Should be able to create comment of a comment via the api. """
        article = create_article()
        comment = Comment(body="I was cool", author=self.user.profile, article=article)
        comment.save()
        url = reverse(
            "articles:comment",
            kwargs={'article_slug':article.slug, "comment_pk":comment.pk}
        )
        response = self.client.post(url, self.sub_comment, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_can_delete_comment(self):
        """ Should be able to delete comment via the api. """
        article = create_article()
        comment = Comment(body="I was cool", author=self.user.profile, article=article)
        comment.save()
        url = reverse(
            "articles:comment",
            kwargs={'article_slug':article.slug, "comment_pk":comment.pk}
        )
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_can_get_article_comments(self):
        """ Should be able to get article comments via the api. """
        article = create_article()
        comment = Comment(body="I was cool", author=self.user.profile, article=article)
        comment.save()
        url = reverse("articles:comments", kwargs={'article_slug':article.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_cannot_comment_unavilable_article(self):
        """ Should not be able to post a comment on an article that does not exist. """
        article = create_article()
        url = reverse("articles:comments", kwargs={'article_slug':article.slug+'not_valid'})
        response = self.client.post(url, self.comment, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_cannot_comment_unavilable_article_comment(self):
        """
        Should not be able to post a
        comment on an comment whose article
        that does not exist. """
        article = create_article()
        comment = Comment(body="I was cool", author=self.user.profile, article=article)
        comment.save()
        url = reverse(
            "articles:comment",
            kwargs={'article_slug':article.slug+'not_valid', 'comment_pk':comment.pk}
        )
        response = self.client.post(url, self.comment, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_cannot_comment_on_an_unavilable_comment(self):
        """ Should not be able to post a comment on an comment that does not exist. """
        article = create_article()
        url = reverse("articles:comment", kwargs={'article_slug':article.slug, "comment_pk":3})
        response = self.client.post(url, self.sub_comment, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_cannot_delete_an_unavilable_comment(self):
        """ Should not be able to post a comment on an comment that does not exist. """
        article = create_article()
        url = reverse("articles:comment", kwargs={'article_slug':article.slug, "comment_pk":3})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_can_get_all_comments(self):
        """ Should be able to get comments for an article. """
        article = create_article()
        url = reverse("articles:comments", kwargs={'article_slug':article.slug})
        response = self.client.get(url)
        content = json.loads(response.content)
        self.assertEqual(len(content.get("comments")), 0)

        comment = Comment(body="I was cool", author=self.user.profile, article=article)
        comment.save()

        url = reverse("articles:comments", kwargs={'article_slug':article.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
