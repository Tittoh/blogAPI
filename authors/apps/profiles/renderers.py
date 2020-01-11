from authors.apps.core.renderers import AuthorsJSONRenderer


class ProfileJSONRenderer(AuthorsJSONRenderer):
    object_label = 'profile'
    object_label_plural = 'profiles'
