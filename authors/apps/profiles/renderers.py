from authors.apps.core.renderers import AuthorsJSONRenderer


class ProfileJSONRenderer(AuthorsJSONRenderer):
    object_label = 'profile'
