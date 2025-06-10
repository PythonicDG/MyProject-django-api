from django.utils.deprecation import MiddlewareMixin
from django.utils import timezone
from rest_framework.exceptions import AuthenticationFailed
from .models import CustomToken
from django.http import JsonResponse
from channels.middleware import BaseMiddleware
from asgiref.sync import sync_to_async
from django.contrib.auth.models import AnonymousUser

class CustomTokenMiddleware(MiddlewareMixin):
    def process_request(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION')

        if not auth_header:
            return  

        if not auth_header.startswith("Token "):
            raise AuthenticationFailed("Invalid Authorization header format")

        key = auth_header.split("Token ")[1]

        try:
            token = CustomToken.objects.get(key=key)
            
        except CustomToken.DoesNotExist:
            return JsonResponse({"message":"Invalid Token"})
            raise AuthenticationFailed("Invalid Token")

        if not token.user.is_active:
            return JsonResponse({"message":"User is not active or has been deleted"})
            raise AuthenticationFailed("User is not active or has been deleted")

        if not token.is_valid():
            token.delete()  
            return JsonResponse({"message":"Token has Expired"})

        request.user = token.user
        request.auth = token



@sync_to_async
def get_user_from_token(token_key):
    try:
        token = CustomToken.objects.get(key=token_key)
        if token.is_valid():
            return token.user
        else:
            return AnonymousUser()
    except CustomToken.DoesNotExist:
        return AnonymousUser()

class TokenAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        from urllib.parse import parse_qs
        query_params = parse_qs(scope["query_string"].decode())
        token_key = query_params.get("token", [None])[0]

        if not token_key:
            scope["user"] = AnonymousUser()
        else:
            user = await get_user_from_token(token_key)
            scope["user"] = user

        return await super().__call__(scope, receive, send)
        
        
            

