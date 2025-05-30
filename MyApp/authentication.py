from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .models import CustomToken

class CustomTokenAuthentication(TokenAuthentication):
    model = CustomToken  # Use your custom token model

    def authenticate_credentials(self, key):
        try:
            token = self.model.objects.get(key=key)
        except self.model.DoesNotExist:
            raise AuthenticationFailed("Invalid token")

        if not token.user.is_active:
            raise AuthenticationFailed("User is not active or has been deleted")

        if not token.is_valid():
            token.delete()
            raise AuthenticationFailed("Token has expired")

        return (token.user, token)
    