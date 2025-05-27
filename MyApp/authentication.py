from rest_framework.authentication import TokenAuthentication
from .models import CustomToken
from rest_framework.exceptions import AuthenticationFailed

class CustomTokenAuthentication(TokenAuthentication):

    def authenticate_credentials(self, key):
        try:
            token = CustomToken.objects.get(key=key)

        except CustomToken.DoesNotExist:
            raise AuthenticationFailed('Invalid token.')

        if not token.user.is_active:
            raise AuthenticationFailed('User inactive or deleted.')

        if not token.is_valid():
            raise AuthenticationFailed('Token has expired.')

        return (token.user, token)





