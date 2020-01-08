import os
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.template.loader import render_to_string
from rest_framework import serializers
from rest_framework import status, generics
from rest_framework import status
from rest_framework.generics import RetrieveUpdateAPIView, CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from .models import User
from django.http import HttpResponse
from rest_framework.views import APIView
from social_django.utils import load_strategy, load_backend
from social_core.backends.oauth import BaseOAuth1, BaseOAuth2
from social_core.exceptions import MissingBackend, AuthAlreadyAssociated
from requests.exceptions import HTTPError
from authors.apps.core.email import SendMail
from django.contrib.auth import get_user_model
from .utils import generate_token
from .renderers import UserJSONRenderer
from .serializers import (
    LoginSerializer, RegistrationSerializer, UserSerializer, SocialSignUpSerializer
)


class RegistrationAPIView(APIView):
    # Allow any user (authenticated or not) to hit this endpoint.
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = RegistrationSerializer

    def post(self, request):
        user = request.data.get('user', {})

        # The create serializer, validate serializer, save serializer pattern
        # below is common and you will see it a lot throughout this course and
        # your own work later on. Get familiar with it.
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        user = get_user_model().objects.filter(
            email=serializer.data.get("email")).first()
        token = generate_token.make_token(user)
        SendMail(
            "email.html",
            {
                'user': user,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': token
            },
            subject="Verify your account",
            to=[user.email]
        ).send()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class VerifyAccount(APIView):
    """ Verify account on vian sent link """

    def get(self, request, uidb64, token):
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        if user is not None and generate_token.check_token(user, token):
            user.is_confirmed = True
            user.save()
            return HttpResponse("Account was verified successfully")
        else:
            return HttpResponse('Activation link is invalid!')

class LoginAPIView(APIView):
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = LoginSerializer

    def post(self, request):
        user = request.data.get('user', {})

        # Notice here that we do not call `serializer.save()` like we did for
        # the registration endpoint. This is because we don't actually have
        # anything to save. Instead, the `validate` method on our serializer
        # handles everything we need.
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class UserRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = UserSerializer

    def retrieve(self, request, *args, **kwargs):
        # There is nothing to validate or save here. Instead, we just want the
        # serializer to handle turning our `User` object into something that
        # can be JSONified and sent to the client.
        serializer = self.serializer_class(request.user)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        user_data = request.data.get('user', {})

        serializer_data = {
            'username': user_data.get('username', request.user.username),
            'email': user_data.get('email', request.user.email),

            'profile': {
                'bio': user_data.get('bio', request.user.profile.bio),
                'image': user_data.get('image', request.user.profile.image)
            }
        }

        # Here is that serialize, validate, save pattern we talked about
        # before.
        serializer = self.serializer_class(
            request.user, data=serializer_data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

class SocialAuthView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = SocialSignUpSerializer
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)

    def create(self, request, *args, **kwargs):
        """
        Override `create` instead of `perform_create` to access request
        request is necessary for `load_strategy`
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        return self.create_token(request, serializer)

    def create_token(self, request, serializer):
        provider = request.data['provider']

        # passing `request` to `load_strategy`,
        # python-social-auth knows to use the Django strategy.
        # `strategy` is a PSA concept for referencing Python frameworks
        # (e.g. Flask, Django, etc.)
        strategy = load_strategy(request)

        # get backend corresponding to our user's social auth provider
        # i.e. Google, Facebook, Twitter
        try:
            backend = load_backend(
                strategy=strategy, name=provider, redirect_uri=None)
        except MissingBackend as e:
            return Response({
                "errors": {
                    "provider": ["Provider not found.", str(e)]
                }

            }, status=status.HTTP_404_NOT_FOUND)

        if isinstance(backend, BaseOAuth1):
            try:
                # Twitter uses OAuth1 and requires that you also pass
                # an `oauth_token_secret` with your authentication request
                token = {
                    'oauth_token': serializer.data['access_token'],
                    'oauth_token_secret': request.data['access_token_secret'],
                }
                return self.get_auth_user(request, backend, token, provider)
            except KeyError:
                return Response({
                    "errors": "provide access_token and/or access_token_secret"

                }, status=status.HTTP_400_BAD_REQUEST)

        elif isinstance(backend, BaseOAuth2):
            # only access token required for oauth2
            token = serializer.data['access_token']
            return self.get_auth_user(request, backend, token, provider)

    def get_auth_user(self, request, backend, token, provider):
        # If this request is made with an authenticated user,
        #  try to associate a social account with it
        authed_user = request.user if not request.user.is_anonymous else None

        try:
            # if `authed_user` is None,
            #   python-social-auth will make a new user,
            # else
            #   this social account will be associated with the user parsed
            user = backend.do_auth(token, user=authed_user)
        except AuthAlreadyAssociated:
            return Response({
                "errors": "That social media account is already in use"
            }, status=status.HTTP_409_CONFLICT)

        return self.serialize_user(user, provider, token)

    def serialize_user(self, user, provider, token):
        if user and user.is_active:
            # if the access token was set to an empty string,
            # then save the access token from the request
            serializer = UserSerializer(user)
            auth_created = user.social_auth.get(provider=provider)
            if not auth_created.extra_data['access_token']:
                auth_created.extra_data['access_token'] = token
                auth_created.save()

            # Set instance since we are not calling `serializer.save()`
            serializer.instance = user
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED,
                            headers=headers)
        else:
            return Response({"errors": "Error with social authentication"},
                status=status.HTTP_400_BAD_REQUEST)

