from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
import json
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from MyApp.models import CustomUser
from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from .models import CustomToken, CustomUser
from django.db import IntegrityError
import pytz
from rest_framework.permissions import IsAuthenticated

@permission_classes(['IsAuthenticated'])
@api_view(['POST'])
def login_view(request):
    if request.method == 'POST':

        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(request, username=username, password=password)
        
        if user is None: 
            return JsonResponse({"message":"usernot Exist"}, status = status.HTTP_404_NOT_FOUND)

        login(request, user)
        try:
            token, created = CustomToken.objects.get_or_create(user=user)

        except IntegrityError:
            token = CustomToken.objects.get(user=user)
            created = False
        
        utc_now = timezone.now()
        utc_now = utc_now.replace(tzinfo=pytz.utc)

        if not created and token.created < utc_now - settings.TOKEN_TTL:

            token.delete()
            token = CustomToken.objects.create(user=request.user)
            token.save()
            return JsonResponse({"message": "Token has been expired", "action": "new Token is generated", "Token": token.key}) 
            
        return JsonResponse({"message": "login success", "user": user.username})

    return JsonResponse({'Message': "Wrong Method"}, status = status.HTTP_405_NOT_FOUND)


@api_view(['POST'])
def logout_view(request):
    if request.method == 'POST':
        logout(request)
        
        return JsonResponse({"message":"logout sucess"})

    return JsonResponse({'message':'wrong method called'})


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
def get_user(request):
    if request.method == 'GET':
        user = request.user

        auth_header = request.META.get('HTTP_AUTHORIZATION',None)

        if auth_header is None:
            return JsonResponse({"message": "Token is not Provided"})

        token = Token.objects.get(user=user)

        now = timezone.now()
        if token.created < now - settings.TOKEN_TTL:
            return JsonResponse({"message":"Token has Expired, Please Log in again"})
        
        return JsonResponse({"username":user.username})
