from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
import json


def login_api_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
        except json.JSONDecodeError:
            username = request.POST.get('username')
            password = request.POST.get('password')

        if not username or not password:
            return JsonResponse({'error': 'Username and password are required.'}, status=400)
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            return JsonResponse({'message':'login successful'}, status=200)
        else:
            return JsonResponse({'error': 'Invalid username or password.'}, status=401)
    return JsonResponse({'error': 'Invalid request method.'}, status=405)



def logout_api_view(request):
    if request.method=='POST':
        if request.user.is_authenticated():
            logout(request)
            return JsonResponse({'message':'logout sucessfull'}, status=200)
        else:
            return JsonResponse({'sucess':False,'message':'No User currenly logged in'})
    else:
            return JsonResponse({'sucess':False,'message':'only post requests are allowed'})
    


def current_user_api_view(request):
    if request.user.is_authenticated:
        user_data = {
            'username': request.user.username,
            'email': request.user.email,
            'is_active': request.user.is_active,
            'phone_number': None
        }
        try:
            if hasattr(request.user,'customuser'):
                user_data['phone_number'] = request.user.customuser.phone_number
        except AttributeError:
            pass

        return JsonResponse({'success':True, 'user':user_data})
    else:
        return JsonResponse({'success':False,'message':'no user currently login'})