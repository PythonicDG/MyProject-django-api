from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.utils import timezone
from django.db import IntegrityError
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework import status
from django.contrib.auth.models import User, Group
from .models import CustomToken, TempModel, CustomUser, Cart, Product, Category
import smtplib
import random
import json
from datetime import datetime
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.utils import timezone
from .models import CustomToken
from rest_framework.permissions import IsAuthenticated, AllowAny

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Cart
from .serializers import CartSerializer, CategorySerializer, ProductSerializer
from rest_framework import viewsets, filters
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from django.shortcuts import render
from .authentication import CustomTokenAuthentication
import threading
from django.contrib.sites.shortcuts import get_current_site
import os
import base64
from django.templatetags.static import static


from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from email.mime.image import MIMEImage
from datetime import datetime
import os

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(request, username=username, password=password)
    if user is None:
        return JsonResponse({"message": "Invalid credentials"}, status=401)

    login(request, user)

    now = timezone.now()
    token = CustomToken.objects.filter(user=user).first()
    
    if token:
        if not token.is_valid():
            token.delete()
            token = CustomToken.objects.create(user=user)
            return JsonResponse({
                "message": "Token has been expired, New Token is generated",
                "token": token.key,
                "user": user.username
            })

    if not token:
        token = CustomToken.objects.create(user=user)

    return JsonResponse({
        "message": "Login successful",
        "token": token.key,
        "user": user.username
    })


@api_view(['POST'])
def logout_view(request):   
    logout(request)
    return JsonResponse({"message": "Logout success"})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([CustomTokenAuthentication])
def get_user(request):
    user = request.user  

    data = {
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email
    }

    return JsonResponse({"user": data})

#send_mail
def send_email(email,otp):
    if email and otp:
        try:
            context = {
                "name":"User",
                "otp":otp,
                "year":datetime.now().year
            }

            html_message = render_to_string('emails/email_template.html',context)

            send_mail(
                subject="Your OTP Code",
                html_message=html_message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
                fail_silently=False
            )

            return JsonResponse({"message":"OTP sent successfully"})

        except Exception as e:
            return JsonResponse({"message": e})

#EmailMessage
def send_mail_class(email,otp,image_url):
    if email and otp:
        try:
            context = {
                "name": "User",
                "otp": otp,
                "year": datetime.now().year,
                "img": image_url
            }
            print(image_url)
            html_message = render_to_string('emails/email_template.html',context)

            mail = EmailMessage(
                subject = "Your OTP Message",
                from_email = settings.EMAIL_HOST_USER,
                to = [email]
            )
            mail.content_subtype = 'html'
            mail.body = html_message
            mail.send()
            print("Congradulations")
            return JsonResponse({"message":"OTP send Successfully"})

        
        
        except Exception as e:
            return JsonResponse({"error":"error"})

#EmailMultiAlternatives
def send_email_alt(email, otp):
    context = {
        "name": "User",
        "otp": otp,
        "year": datetime.now().year,
        "img": "cid:search_image"  
    }

    html_message = render_to_string('emails/email_template.html', context)

    email_msg = EmailMultiAlternatives(
        subject="Your OTP Code",
        body="", 
        from_email= settings.EMAIL_HOST_USER,  # replace with settings.EMAIL_HOST_USER if you want
        to=[email],
    )

    email_msg.attach_alternative(html_message, "text/html")

    image_path = r'C:\Users\dipak\Desktop\Company_work\Project1\MyProject\MyApp\search.png'  
    with open(image_path, 'rb') as img_file:
        mime_image = MIMEImage(img_file.read())
        mime_image.add_header('Content-ID', '<search_image>')  # must match context img
        mime_image.add_header('Content-Disposition', 'inline', filename='search.png')
        email_msg.attach(mime_image)

    email_msg.send()


#sending mail using thread
def send_mail_thread(email,otp):
    print("inside the threaidng")
    thread = threading.Thread(target=send_email_alt, args=(email,otp))
    thread.start()



@api_view(['POST'])
@permission_classes([])
def register_email(request):
    email = request.data.get('email')
    if not email:
        return JsonResponse({'message': 'Email is required'})

    otp = "".join([str(random.randint(0, 9)) for _ in range(6)])
    created_at = timezone.now()

    TempModel.objects.update_or_create(
        email=email,
        defaults={'otp': otp, 'created_at': created_at}
    )
    image_url = request.build_absolute_uri(static('images/search.png'))
    
    send_mail_thread(email, otp)
    return JsonResponse({'message': 'OTP sent successfully'})


@api_view(['POST'])
@permission_classes([])
def verify_otp(request):
    email = request.data.get('email')
    otp = request.data.get('otp')

    try:
        user = TempModel.objects.get(email=email)

    except TempModel.DoesNotExist:
        return JsonResponse({'message': 'Invalid email'})

    expiry_time = user.created_at + timezone.timedelta(minutes=10)

    if expiry_time < timezone.now():
        return JsonResponse({'message': 'OTP expired'})

    if user.otp != otp:
        return JsonResponse({'message': 'Invalid OTP'})

    return JsonResponse({'message': 'OTP verified'})


@api_view(['POST'])
def registration(request):
    data = json.loads(request.body)

    username = data.get('username')
    password = data.get('password')
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    phone_number = data.get('phone_number')
    email = data.get('email')

    if CustomUser.objects.filter(email=email).exists():
        return JsonResponse({'message': 'Email already exists'})

    try:
        TempModel.objects.get(email=email)
        
    except TempModel.DoesNotExist:
        return JsonResponse({'message': 'Email not verified'})

    user = CustomUser(
        username=username,
        email=email,
        first_name=first_name,
        last_name=last_name,
        phone_number=phone_number
    )
    user.set_password(password)
    user.save()

    return JsonResponse({'message': 'Registration successful'})

#26-05-2025

def fetch_groups(request):
    if request.method == 'GET':
        group_id = request.GET.get('group_id')
        group_name = request.GET.get('group_name')
        search = request.GET.get('search')
        filter_by = request.GET.get('filter_by')
        get_users = request.GET.get('get_users')

        if group_id:    
            try:
                groups = Group.objects.get(id=group_id)

                users = User.objects.filter(groups=groups)

                data = []

                for i in users:
                    data.append(i.username)

                return JsonResponse({"group name": groups.name, 'users': data})

            except Group.DoesNotExist:
                return JsonResponse({"message":"Group ID does not exist"})

        elif search:
            try:
                user = User.objects.get(username=search)

                data = {
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email
                }

                return JsonResponse({"Username":user.username,"Data":data})
            
            except User.DoesNotExist:
                return JsonResponse({"Message":"User Does Not Exist"})

        elif filter_by:
            users = User.objects.filter(is_active=filter_by)

            data =[
                {
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email
                }
                for user in users
            ]

            return JsonResponse({"users":data})
        
        else:
            groups = Group.objects.all()

            data = [
                {
                    'id': group.id,
                    'name': group.name,
                    'users': list(User.objects.filter(groups=group).values('username','first_name','last_name'))
                }
                for group in groups
            ]

            return JsonResponse(data, safe=False)

@api_view(['DELETE'])
def delete_user(request,username):
    try:
        user = User.objects.get(username=username)
        user.delete()
        
        return JsonResponse({"User Deleted Successfully":username})
    
    except User.DoesNotExist:
        return JsonResponse({"error":"User Does Not Exist"})    

@api_view(['GET'])
def get_users(request):
    users = User.objects.all()

    users_list = []
    
    for user in users:
        users_list.append(user.first_name)

    users_list.sort()

    return JsonResponse({"List of Users sorted by Alphabetical Order":users_list})


@api_view(['PUT'])
def update_user(request, username):
    try:
        user = User.objects.get(username=username)

    except User.DoesNotExist:
        return JsonResponse({"message":"User not found"})
    
    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
            
        except Exception as e:
            return JsonResponse({"Error":e})

        first_name = data.get('first_name')
        last_name = data.get('last_name')
        phone_number = data.get('phone_number')

        if first_name:
            user.first_name = first_name
            user.save()
        
        if last_name:
            user.last_name = last_name
            user.save()

        if phone_number:
            user.phone_number = phone_number
            user.save()
        
        return JsonResponse({"message":"data updated succesfully"})
    
    return JsonResponse({"message":"data updatation is failed"})


#Cart Class Based Views
def cart_to_dict(cart):
    return {
        "id": cart.id,
        "name": cart.name,
        "price": cart.price,
    }

class CartListCreateAPIView(APIView):
    def get(self, request):
        carts = Cart.objects.all()

        filter_backends = [filters.SearchFilter]
        search_fields = ['name']
        data = []
        
        for i in carts:
            data.append(cart_to_dict(i))

        return Response(data)

    def post(self, request):
        data = request.data

        try:
            cart = Cart.objects.create(
                name=data["name"],
                price=data["price"],
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(cart_to_dict(cart), status=status.HTTP_201_CREATED)


class CartDetailAPIView(APIView):
    def get_object(self, id):
        try:
            return Cart.objects.get(id=id)

        except Cart.DoesNotExist:
            return None

    def get(self, request, id):
        cart = self.get_object(id)

        if not cart:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        return Response(cart_to_dict(cart))

    def put(self, request, id):
        cart = self.get_object(id)

        if not cart:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        data = request.data

        if "name" in data:
            cart.name = data["name"]

        if "price" in data:
            cart.price = data["price"]

        try:
            cart.save()

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(cart_to_dict(cart))

    def delete(self, request, id):
        cart = self.get_object(id)

        if not cart:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        cart.delete()
        return Response("Item deleted successfully",status=status.HTTP_204_NO_CONTENT)


#CRUD operations using Model View Set

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()

    serializer_class = CategorySerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    
    serializer_class = ProductSerializer

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]

    search_fields = ['name']

    ordering_fields = ['name']

    def get_queryset(self):
        queryset = Product.objects.all()

        category_id = self.request.query_params.get('category')

        if category_id:
            queryset = queryset.filter(categories__id=category_id)

        return queryset



#testing the template

def preview_email(request):
    context = {
        "name": "Dipak",
        "otp": "123456",
        "year": datetime.now().year
    }
    return render(request, 'emails/email_template.html', context)


#Order and Payment
