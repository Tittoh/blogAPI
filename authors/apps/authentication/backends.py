# import jwt
#
# from django.conf import settings
#
# from rest_framework import authentication, exceptions
#
# from .models import User

import jwt

from django.conf import settings

from rest_framework import authentication, exceptions

from .models import User

class JWTAuthentication:
    """ JWTAuthentication implement jwt authentication. """

    def authenticate(self, request):
        pass

