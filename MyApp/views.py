from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from django.db import IntegrityError
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework import status
from django.contrib.auth.models import User, Group
from .models import CustomToken, TempModel, CustomUser
import smtplib
import random
import json
import datetime

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


def send_mail(email,otp):
    if email and otp:
        try:
            s = smtplib.SMTP('smtp.gmail.com', 587)
            s.starttls()
            s.login('dipakgaikwadms@gmail.com', 'epfgkbrqivwyxsbc')
            s.sendmail('dipakgaikwadmg@gmail.com',email,otp)
            s.quit()
            print("Success")

        except Exception as e:
            return JsonResponse({"message": e})

@api_view(['POST'])
def registration(request):
    username = request.data.get('username')
    password = request.data.get('password')
    email = request.data.get('email')
    first_name = request.data.get('first_name')
    last_name = request.data.get('last_name')
    otp = "".join([str(random.randint(0, 9)) for _ in range(6)])
    phone_number = request.data.get('phone_number')

    if TempModel.objects.filter(username=username).exists():
            instance = TempModel.objects.get(username=username)
            instance.password = password
            instance.email = email
            instance.otp = otp
            instance.first_name = first_name
            instance.save()

            send_mail(email, otp)

            return JsonResponse({"message": "User Alredy Exist","Action": "OTP send Successfully"})
    created_at = timezone.now()

    temp_model_instance = TempModel(
                    username = username, 
                    password = password, 
                    otp = otp,
                    email = email, 
                    first_name = first_name, 
                    last_name = last_name,
                    phone_number = phone_number,
                    created_at = created_at
                    )
    temp_model_instance.save()

    send_mail(email,otp)

    return JsonResponse({'username': 'Data saved Successfully'})

@api_view(['POST'])
def verify_otp(request):
    data = json.loads(request.body)
    email = data.get('email')
    otp = data.get('otp')
    
    try:
        user = TempModel.objects.get(email=email)

    except TempModel.DoesNotExist as e:
        return JsonResponse({"message":"wrong email provided"})

    expiry_ = user.expiry_time()
    
    if expiry_ < timezone.now():
        return JsonResponse({"message": "OTP is expired", "Action": "Please register again"})

    if otp == user.otp:
        if CustomUser.objects.filter(username=user.username):

            return JsonResponse({"message": "email already Exists"})

        custom_user_model = CustomUser(
            username = user.username,
            first_name = user.first_name,
            last_name = user.last_name,
            phone_number = user.phone_number,
            email = user.email
        )
        custom_user_model.set_password(user.password)
        custom_user_model.save()

        return JsonResponse({"message": "Email Verified Successfully", 'email': email})

    return JsonResponse({"message": "Wrong OTP", 'email': email})
    
@api_view(['GET'])
def get_group_info(request):
    groups = Group.objects.all()
    type_groups = type(groups)
    
    for group in groups:
        users = group.user_set.all()

        group_data = {
            "Group name": group.name,
            "users": list(users.values('id','username'))
        }

    return JsonResponse({"data":group_data})




