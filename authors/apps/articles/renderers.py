import json
from rest_framework.renderers import JSONRenderer
from authors.apps.core.renderers import AuthorsJSONRenderer


class ArticleJSONRenderer(JSONRenderer):
    charset = 'utf-8'

    def render(self, data, media_type=None, renderer_context=None):
        if data is not None:

            if isinstance(data, dict):
                return json.dumps({
                    'article': data
                })
            return json.dumps({
                'articles': data,
                'articlesCount': len(data)
            })
        return json.dumps({
            "article": 'No article found.'
        })

class CommentJSONRenderer(AuthorsJSONRenderer):
    """ renders comments"""
    object_label = "comment"
    object_label_plural = 'comments'

class FavoriteJSONRenderer(AuthorsJSONRenderer):
    charset = 'utf-8'
    object_label = "favorite"
    object_label_plural = 'favorites'


class RateJSONRenderer(JSONRenderer):
    charset = 'utf-8'

    def render(self, data, media_type=None, renderer_context=None):
        """
        Render the ratings in a structured manner for the end user.
        """
        return json.dumps({
            'rate': data,
        })
