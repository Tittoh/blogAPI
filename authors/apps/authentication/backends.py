""" Implements jwt.  """

import jwt

from django.conf import settings

from rest_framework import authentication, exceptions

from .models import User

class JWTAuthentication(authentication.BaseAuthentication):
    """ JWTAuthentication implement jwt authentication. """
    authentication_header_prefix='Bearer'

    def authenticate(self, request):
        """ Authenticate the request and return a two-tuple of (user, token). or None """

        # get token
        authentication_header = authentication.get_authorization_header(request).split()
        if not authentication_header:
            return None

        if len(authentication_header) == 1:
            raise  exceptions.AuthenticationFailed(
                "Invalid Authorization header. No credentials provided."
            )


        if len(authentication_header) > 2:
            msg = 'Invalid Authorization header. Credentials string should not contain spaces.'
            raise exceptions.AuthenticationFailed(msg)

        prefix = authentication_header[0].decode('utf-8')
        token = authentication_header[1].decode('utf-8')
        if prefix.lower() != self.authentication_header_prefix.lower():
            raise exceptions.AuthenticationFailed("Invalid token")

        return self.authenticate_user(request, token)

    def authenticate_user(self, request, token):
        """  Returns an active user that matches the payload's user id and email. """
        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY)
        except jwt.ExpiredSignature:
            msg = 'Signature has expired.'
            raise exceptions.AuthenticationFailed(msg)
        except jwt.DecodeError:
            msg = 'Error decoding signature.'
            raise exceptions.AuthenticationFailed(msg)
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed()
        try:
            user = User.objects.get(pk=payload['id'])
        except User.DoesNotExist:
            msg = 'No user matching this token was found.'
            raise exceptions.AuthenticationFailed(msg)
        if not user.is_active:
            msg = 'User account is disabled.'
            raise exceptions.AuthenticationFailed(msg)
        return (user, token)

