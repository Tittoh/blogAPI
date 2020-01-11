from django.shortcuts import render
from rest_framework import status, mixins, viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny, IsAuthenticated
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.response import Response
from rest_framework.generics import RetrieveAPIView, CreateAPIView
from .serializers import ArticleSerializer, RateSerializer
from .renderers import RateJSONRenderer, ArticleJSONRenderer
from .models import Article, Rate
from django.db.models import Avg

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
        article = request.data.get('article', {})
        serializer = self.serializer_class(data=article)
        serializer.is_valid(raise_exception=True)
        serializer.save(author=request.user.profile)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request):
        """
        Get all articles
        """
        queryset = Article.objects.all()
        serializer = self.serializer_class(
            queryset, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

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
