import re
from django.contrib.auth import authenticate
from django.core.validators import RegexValidator
from django.contrib.auth.tokens import default_token_generator
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from authors.apps.profiles.serializers import ProfileSerializer
from .models import Article, Rate, Comment, Tag
from .utils import TagField

class RecursiveSerializer(serializers.Serializer):
   def to_representation(self, value):
       serializer = self.parent.parent.__class__(value, context=self.context)
       return serializer.data


class ArticleSerializer(serializers.ModelSerializer):
    """
    Serializer to map the Model format to Json format
    """
    title = serializers.CharField(required=True)
    body = serializers.CharField(required=True)
    description = serializers.CharField(required=True)
    slug = serializers.SlugField(required=False)
    image_url = serializers.URLField(required=False)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    favorited = serializers.SerializerMethodField(method_name="is_favorited")
    favoriteCount = serializers.SerializerMethodField(
        method_name='get_favorite_count')
    author = ProfileSerializer(read_only=True)
    likes = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    dislikes = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    likes_count = serializers.SerializerMethodField()
    dislikes_count = serializers.SerializerMethodField()
    average_rating = serializers.FloatField(required=False, read_only=True)
    tagList = TagField(many=True, required=False, source='tags')

    class Meta:
        model = Article
        fields = ['title', 'slug', 'body',
            'description', 'image_url', 'created_at', 'updated_at',
                  'author', 'likes', 'dislikes','average_rating',
                  'likes_count', 'dislikes_count', 'favorited', 'favoriteCount', 'tagList',]
    
    def get_favorite_count(self, instance):
        return instance.users_favorites.count()

    def is_favorited(self, instance):
        username = self.context.get('request').user.username
        if instance.users_favorites.filter(user__username=username).count() == 0:
            return False
        return True
    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_dislikes_count(self, obj):
        return obj.dislikes.count()

    def create(self, validated_data):
        tags = validated_data.pop('tags', [])

        article = Article.objects.create(**validated_data)

        for tag in tags:
            article.tags.add(tag)

        return article

    def validate(self, data):
        # The `validate` method is used to validate the title,
        # description and body
        title = data.get('title', None)
        description = data.get('description', None)

        return data

class CommentSerializer(serializers.ModelSerializer):
    """Handles serialization and deserialization of Comments objects."""
    author = ProfileSerializer(required=False)

    createdAt = serializers.SerializerMethodField(method_name='get_created_at')
    updatedAt = serializers.SerializerMethodField(method_name='get_updated_at')

    thread = RecursiveSerializer(many=True, read_only=True)
    class Meta:
        model = Comment
        fields = (
            'id',
            'author',
            'body',
            'createdAt',
            'updatedAt',
            'thread'
        )

    def create(self, validated_data):
        article = self.context['article']
        author = self.context['author']
        parent = self.context.get('parent', None)
        return Comment.objects.create(
            author=author, article=article, parent=parent, **validated_data
        )

    def get_created_at(self, instance):
        """ return created_time """
        return instance.created_at.isoformat()

    def get_updated_at(self, instance):
        """ return updated_at """
        return instance.updated_at.isoformat()
    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_dislikes_count(self, obj):
        return obj.dislikes.count()

class RateSerializer(serializers.Serializer):
    """Serializers registration requests and creates a new rate."""

    rate = serializers.IntegerField(required=True)

    def validate(self, data):
        """Check that rate is valid"""
        rating = data.get('rate')
        if rating == '':
            raise serializers.ValidationError('Rate is required.')
        # Validate the rate is between 0 and 5.
        if rating < 0 or rating > 5:
            raise serializers.ValidationError(
                'Rate should be from 0 to 5.')

        return {"rate": rating}

class TagSerializer(serializers.ModelSerializer):
    """
    Define the tag serializer
    """
    class Meta:
        model = Tag
        fields = ('tag',)

    def to_representation(self, obj):
        return obj.tag
