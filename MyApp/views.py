from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from django.db import IntegrityError
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework import status

from .models import CustomToken

@api_view(['POST'])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(request, username=username, password=password)
    if user is None:
        return JsonResponse({"message": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)

    login(request, user)

    try:
        token, created = CustomToken.objects.get_or_create(user=user)
    except IntegrityError:
        token = CustomToken.objects.get(user=user)
        created = False

    now = timezone.now()

    if not created and (not token.expiry_time or token.expiry_time < now):
        token.delete()
        token = CustomToken.objects.create(user=user)
        token.save()
        return JsonResponse({
            "message": "Token has expired",
            "action": "New token generated",
            "Token": token.key
        })


    return JsonResponse({"message": "Login success", "user": user.username})


@api_view(['POST'])
def logout_view(request):
    logout(request)
    return JsonResponse({"message": "Logout success"})


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
def get_user(request):
    user = request.user
    auth_header = request.META.get('HTTP_AUTHORIZATION')

    if auth_header is None:
        return JsonResponse({"message": "Token not provided"})

    token = get_object_or_404(CustomToken, user=user)
    now = timezone.now()
    
    if token.expiry_time < now:
        return JsonResponse({"message": "Token has expired, please log in again"})

    return JsonResponse({"username": user.username})
