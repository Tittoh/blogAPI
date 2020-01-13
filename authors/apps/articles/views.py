""" Views for django Articles. """
from django.shortcuts import render
from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework import generics
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, AllowAny
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status, mixins, viewsets
from rest_framework.generics import RetrieveAPIView, CreateAPIView
from rest_framework.pagination import PageNumberPagination
from authors import settings
from .models import Article, Rate, Comment, Tag
from .serializers import ArticleSerializer, CommentSerializer, RateSerializer, TagSerializer
from .renderers import ArticleJSONRenderer, CommentJSONRenderer, RateJSONRenderer, FavoriteJSONRenderer

class LikesAPIView(APIView):
    permission_classes = (IsAuthenticatedOrReadOnly, )
    renderer_classes = (ArticleJSONRenderer, )
    serializer_class = ArticleSerializer

    def put(self, request, slug):
        serializer_context = {'request': request}

        try:
            serializer_instance = Article.objects.get(slug=slug)
        except Article.DoesNotExist:
            raise NotFound("An article with this slug does not exist")

        if serializer_instance in Article.objects.filter(dislikes=request.user):
            serializer_instance.dislikes.remove(request.user)

        serializer_instance.likes.add(request.user)

        serializer = self.serializer_class(
            serializer_instance, context=serializer_context, partial=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class DislikesAPIView(APIView):
    permission_classes = (IsAuthenticatedOrReadOnly, )
    renderer_classes = (ArticleJSONRenderer, )
    serializer_class = ArticleSerializer

    def put(self, request, slug):
        serializer_context = {'request': request}

        try:
            serializer_instance = Article.objects.get(slug=slug)
        except Article.DoesNotExist:
            raise NotFound("An article with this slug does not exist")

        if serializer_instance in Article.objects.filter(likes=request.user):
            serializer_instance.likes.remove(request.user)

        serializer_instance.dislikes.add(request.user)

        serializer = self.serializer_class(
            serializer_instance,  context=serializer_context, partial=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

class RateAPIView(CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = RateSerializer
    renderer_classes = (RateJSONRenderer,)

    def create(self, request, slug):
        """ Rating view"""
        ratings = request.data.get("rate", {})
        # Filter articles with the given slug
        try:
            article = Article.objects.filter(slug=slug).first()

        except Article.DoesNotExist:
            return Response({"errors":{"message":["Article doesnt exist."]}})

       # Check if article is none
        if article is None:
            return Response({"errors":{"message":["Article doesnt exist."]}},
                    404)

        # Serialize rate model
        serializer = self.serializer_class(data=ratings)
        # Check for validation errors
        serializer.is_valid(raise_exception=True)
        rate = serializer.data.get('rate')
        # Filter rate table to check if record with given article and user
        # exist.
        rating = Rate.objects.filter(article=article,
                rater=request.user.profile).first()

        if not rating:
            """ If it doesnt exist create an new record."""
            rating = Rate(article=article, rater=request.user.profile, ratings=rate)
            rating.save()
            # get the averages ratings of the article.
            avg_ratings = Rate.objects.filter(article=article).aggregate(Avg('ratings'))
            return Response({"response":{"message":["Successfull."],
                "avg_ratings":avg_ratings
                }}, status=status.HTTP_201_CREATED)

        # If exist check if the user has exceed rating counter
        if rating.counter > 3: 
            """Allow rating if counter is less than 3."""
            return Response({"errors":{"message":["You are only allowed to"
            "rate 3 times"]}}, status=status.HTTP_403_FORBIDDEN)

        rating.ratings = rate
        rating.save()
        # Get the average ratings of the article.
        avg = Rate.objects.filter(article=article).aggregate(Avg('ratings'))
        return Response({"avg":avg}, status=status.HTTP_201_CREATED)

class ArticleAPIView(mixins.CreateModelMixin,
                     mixins.ListModelMixin,
                     mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    This class defines the create behavior of our articles.
    """
    lookup_field = 'slug'
    queryset = Article.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly, )
    serializer_class = ArticleSerializer
    renderer_classes = (ArticleJSONRenderer, )

    def create(self, request):
        """
        Create an article
        """
        serializer_context = {'request': request}
        article = request.data.get('article', {})
        serializer = self.serializer_class(
            data=article, context=serializer_context)
        serializer.is_valid(raise_exception=True)
        serializer.save(author=request.user.profile)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, slug):
        """
        Get one article
        """
        serializer_context = {'request': request}
        try:
            serializer_instance = self.queryset.get(slug=slug)
        except Article.DoesNotExist:
            raise NotFound('Article not found')

        serializer = self.serializer_class(
            serializer_instance,
            context=serializer_context

        )

        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, slug):
        """
        Edit an article
        """
        serializer_context = {'request': request}
        try:
            serializer_instance = self.queryset.get(slug=slug)
        except Article.DoesNotExist:
            raise NotFound('Artiicle not found')

        if not serializer_instance.author.id == request.user.profile.id:
            raise PermissionDenied(
                'You do not have permission to edit this article')

        serializer_data = request.data.get('article', )

        serializer = self.serializer_class(
            serializer_instance,
            context=serializer_context,
            data=serializer_data,
            partial=True
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, slug):
        """
        Delete an article
        """
        try:
            article = self.queryset.get(slug=slug)
        except Article.DoesNotExist:
            raise NotFound('Article not found')

        if article.author_id == request.user.profile.id:
            article.delete()
        else:
            raise PermissionDenied(
                'You do not have permission to delete this article')

        return Response(None, status=status.HTTP_204_NO_CONTENT)

class CommentsListCreateAPIView(generics.ListCreateAPIView):
    lookup_field = 'article__slug'
    lookup_url_kwarg = 'article_slug'
    permission_classes = (IsAuthenticated,)
    serializer_class = CommentSerializer
    renderer_classes = (CommentJSONRenderer,)

    queryset = Comment.objects.select_related(
        'article', 'article__author', 'article__author__user',
        'author', 'author__user'
    )

    def filter_queryset(self, queryset):
        filters = {self.lookup_field: self.kwargs[self.lookup_url_kwarg]}
        return queryset.filter(**filters).filter(parent=None)

    def create(self, request,  article_slug=None):
        data = request.data.get('comment', {})
        context = {'author': request.user.profile}

        try:
            context['article'] = Article.objects.get(slug=article_slug)
        except Article.DoesNotExist:
            raise NotFound('An article with this slug does not exist.')

        serializer = self.serializer_class(data=data, context=context)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

class CommentsCreateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView, generics.CreateAPIView):
    permission_classes = (IsAuthenticated,)
    lookup_url_kwarg = 'comment_pk'
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    renderer_classes = (CommentJSONRenderer,)

    def destroy(self, request, article_slug=None, comment_pk=None):
        try:
            comment = Comment.objects.get(pk=comment_pk)
        except Comment.DoesNotExist:
            raise NotFound('A comment with this ID does not exist.')

        comment.delete()

        return Response(None, status=status.HTTP_204_NO_CONTENT)

    def create(self, request, article_slug=None, comment_pk=None):
        data = request.data.get('comment', {})
        context = {'author': request.user.profile}

        try:
            context['article'] = Article.objects.get(slug=article_slug)
        except Article.DoesNotExist:
            raise NotFound('An article with this slug does not exist.')

        try:
            # get the parent comment
            context['parent'] = comment = Comment.objects.get(pk=comment_pk)
        except Comment.DoesNotExist:
            raise NotFound('A comment with this ID does not exist.')

        serializer = self.serializer_class(data=data, context=context)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

class FavoriteAPIView(APIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (FavoriteJSONRenderer,)
    serializer_class = ArticleSerializer
    queryset = Article.objects.all()

    def post(self, request, slug):
        """
        Method that favorites articles.
        """
        serializer_context = {'request': request}
        try:
            article = self.queryset.get(slug=slug)
        except Article.DoesNotExist:
            raise NotFound("An article with this slug does not exist")

        request.user.profile.favorite(article)

        serializer = self.serializer_class(
            article,
            context=serializer_context
        )
        return Response(serializer.data,  status=status.HTTP_201_CREATED)

    def delete(self, request, slug):
        """
        Method that favorites articles.
        """
        serializer_context = {'request': request}
        try:
            article = self.queryset.get(slug=slug)
        except Article.DoesNotExist:
            raise NotFound("An article with this slug does not exist")

        request.user.profile.unfavorite(article)

        serializer = self.serializer_class(
            article,
            context=serializer_context
        )
        return Response(serializer.data,  status=status.HTTP_200_OK)

class TagAPIView(generics.ListAPIView):
    queryset = Tag.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = TagSerializer

    def list(self, request):
        serializer_data = self.get_queryset()
        serializer = self.serializer_class(serializer_data, many=True)

        return Response({'tags': serializer.data}, status.HTTP_200_OK)

class FilterSearchAPIView(generics.ListAPIView):
    permission_classes = (IsAuthenticatedOrReadOnly, )
    search_list = ['title', 'body',
                   'description', 'author__user__username', 'tags__tag']
    filter_list = ['title', 'author__id', 'tags__tag']
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter, )
    filter_fields = filter_list
    search_fields = search_list
