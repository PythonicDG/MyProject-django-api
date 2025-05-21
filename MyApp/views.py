from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
import json
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from django.contrib.sessions.models import Session



@api_view(['POST'])
def login_view(request):
    if request.method == 'POST':

        data = json.loads(request.body)

        username = data.get('username')
        password = data.get('password')
        user = authenticate(request,username=username,password=password)
        
        if user is not None:
            login(request,user)
            return JsonResponse({"message":"login success","user":username})
        else:
            return JsonResponse({"message":"usernot Exist"},status=status.HTTP_404_NOT_FOUND)

    return JsonResponse({'Message':"Wrong Method"},status= status.HTTP_405_NOT_FOUND)



@api_view(['POST'])
def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return JsonResponse({"message":"logout sucess"})
    else:
        return JsonResponse({'message':'wrong method called'})



