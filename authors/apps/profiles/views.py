from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import serializers, status
from rest_framework.views import APIView
from rest_framework.exceptions import NotFound
from .models import Profile
from .renderers import ProfileJSONRenderer
from .serializers import ProfileSerializer
from .exceptions import ProfileDoesNotExist

import json


class ProfileRetrieveAPIView(RetrieveAPIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (ProfileJSONRenderer,)
    serializer_class = ProfileSerializer

    def retrieve(self, request, username, *args, **kwargs):
        try:
            profile = Profile.objects.select_related('user').get(
                user__username=username
            )

        except Profile.DoesNotExist:
            raise ProfileDoesNotExist

        serializer = self.serializer_class(profile)

        return Response(serializer.data, status=status.HTTP_200_OK)

class ProfileFollowAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (ProfileJSONRenderer,)
    serializer_class = ProfileSerializer

    def delete(self, request, username):
        ''' The current user is able to unfollow another user's profile. '''
        follower = request.user.profile

        # Get the profile of user being followed
        try:
            followed = Profile.objects.get(user__username=username)
        except Profile.DoesNotExist:
            raise NotFound('The user with this profile does not exist')

        # The function unfollow takes the followed user
        follower.unfollow(followed)

        serializer = self.serializer_class(follower, context={
            'request': request})

        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, username):
        ''' The current user is able to follow another user's profile. '''
        follower = request.user.profile

        # Get the profile of user being followed
        try:
            followed = Profile.objects.get(user__username=username)
        except Profile.DoesNotExist:
            raise NotFound('The user with this profile does not exist')

        # A user cannot follow themselves
        if follower.pk is followed.pk:
            raise serializers.ValidationError('You cannot follow yourself')

        # The function follow takes the followed user
        follower.follow(followed)

        serializer = self.serializer_class(follower, context={
            'request': request})

        return Response(serializer.data, status=status.HTTP_200_OK)


class FollowersAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (ProfileJSONRenderer,)
    serializer_class = ProfileSerializer

    def get(self, request, username):
        user = request.user.profile
        profile = Profile.objects.get(user__username=username)

        followers = user.get_followers(profile)
        serializer = self.serializer_class(followers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class FollowingAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (ProfileJSONRenderer,)
    serializer_class = ProfileSerializer

    def get(self, request, username):
        user = request.user.profile
        profile = Profile.objects.get(user__username=username)

        following = user.get_following(profile)
        serializer = self.serializer_class(following, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
