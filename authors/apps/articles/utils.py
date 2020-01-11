from rest_framework import serializers

from .models import Tag
from django.utils.text import slugify

class TagField(serializers.RelatedField):
    """
    Tag field helper class
    """
    def get_queryset(self):
        result = Tag.objects.all()
        return result

    def to_internal_value(self, data):
        tag, created = Tag.objects.get_or_create(
            tag=data, slug=slugify(data.lower())
        )
        return tag

    def to_representation(self, value):
        return value.tag
