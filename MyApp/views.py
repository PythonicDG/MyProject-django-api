from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.utils import timezone
from django.db import IntegrityError
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework import status
from django.contrib.auth.models import User, Group
from .models import CustomToken, TempModel, CustomUser, Cart, Product, Category, Order, Payment, OrderedItem, Customer, Storage
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
from .serializers import CartSerializer, CategorySerializer, ProductSerializer, OrderSerializer
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
from django.core.paginator import Paginator
from rest_framework.decorators import api_view
from rest_framework.response import Response
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from decimal import Decimal

import pandas as pd
from django.http import HttpResponse
from rest_framework.decorators import api_view
from django.http import HttpResponse
import pandas as pd
import io

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
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def place_order(request):
    data = request.data
    user = request.user

    customer, created = Customer.objects.get_or_create(
        user=user,
        defaults={
            'customer_email': data.get('customer_email', ''),
            'customer_name': data.get('customer_name', '')
        }
    )

    order = Order.objects.create(
        user=user,
        customer=customer,
        customer_name=customer.customer_name,
        customer_email=customer.customer_email
    )

    for item in data.get('items', []):
        try:
            product = Product.objects.get(id=item['product_id'], is_active=True)
        except Product.DoesNotExist:
            order.delete()
            return Response({'error': f"Product with ID {item['product_id']} not found or inactive"}, status=400)

        OrderedItem.objects.create(
            order=order,
            product=product,
            qty=item['qty'],
            price=product.price
        )

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "orders",
        {
            "type": "send_order_notification",
            "data": {
                "message": f"New order placed (Order ID: {order.id})"
            }
        }
    )

    return JsonResponse({'message': 'Order placed successfully', 'order_id': order.id})


@api_view(['POST'])
def make_payment(request):
    data = request.data
    try:
        order = Order.objects.get(id=data['order_id'])
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=404)

    if order.is_paid:
        return Response({'message': 'Payment already made'})

    amount = order.total_amount()

    if 'order_id' not in data or 'transaction_id' not in data:
        return Response({'error': 'Invalid payment data'}, status=400)
        
    Payment.objects.create(order=order, amount=amount, transaction_id=data['transaction_id'])
    order.is_paid = True
    order.status = 'Served'
    order.save()

    item_details = []
    for item in order.ordered_items.all():
        print("we are inside the loop")
        item_total = item.qty * item.price
        item_details.append({
            'product_name': item.product.name,
            'qty': item.qty,
            'unit_price': float(item.price),
            'total': float(item_total)
        })

    return Response({
        'status': 'Payment Successful',
        'order_id': order.id,
        'customer': order.customer.customer_name,
        'items': item_details,
        'total_amount': float(amount),
        'paid_at': order.payment.payment_time
    })



@api_view(['POST'])
def update_order_status(request):
    data = request.data
    
    order = Order.objects.get(id = data['order_id'])

    status = data['status']
    if status not in dict(Order.STATUS_CHOICES):
        return JsonResponse({"error":"Invalid status"})
    
    order.status = status
    order.save()

    return JsonResponse({"message":"status updated"})

@api_view(['POST'])
def remove_item(request):
    data = request.data
    order = Order.objects.get(id=data['order_id'])

    try:
        item = OrderedItem.objects.get(order=order, product__id=data['product_id'])
        item.delete()
        return Response({'message': 'Item removed'})
    except OrderedItem.DoesNotExist:
        return Response({'error': 'Item not found in order'}, status=404)


@api_view(['POST'])
def cancel_order(request):
    data = request.data
    order = Order.objects.get(id=data['order_id'])

    order.status = 'cancelled'
    order.save()
    return Response({'status': 'Order Cancelled'})

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().order_by('-created_at')
    serializer_class = OrderSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['customer_name', 'status']
    ordering_fields = ['created_at', 'status']


@api_view(['GET'])
def get_orders(request):
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 5))
    orders = Order.objects.all().order_by('-created_at')
    paginator = Paginator(orders, page_size)
    page_obj = paginator.get_page(page)

    result = []
    for order in page_obj:
        items = [{
            'product_id': i.product.id,
            'product_name': i.product.name,
            'qty': i.qty,
            'price': float(i.price)
        } for i in order.ordered_items.all()]
        
        result.append({
            'order_id': order.id,
            'customer_name': order.customer_name,
            'status': order.status,
            'is_paid': order.is_paid,
            'created_at': order.created_at,
            'items': items,
            'total': float(order.total_amount())
        })

    return Response({
        'orders': result,
        'page': page,
        'total_pages': paginator.num_pages,
        'total_orders': paginator.count
    })


@api_view(['GET'])
def download_excel(request):
    model_name = request.GET.get('name')

    if not model_name:
        return Response("Please provide Model Name ")

    model = eval(f"{model_name}.objects.all().values()")
    df = pd.DataFrame(list(model))

    file_path = os.path.join(settings.MEDIA_ROOT, 'excel_files', f'{model_name}.xlsx')
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    df.to_excel(file_path, index=False)

    return JsonResponse({"message": "file saved successfully", "path": file_path})

@api_view(['POST'])
def upload_excel(request):
    file = request.FILES.get('file')

    if not file:
        return JsonResponse({"message": "Please upload a valid file"})

    #excel_file = io.BytesIO(file.read())
    df = pd.read_excel(file)

    errors = []
    category_names = list(Category.objects.values_list('name', flat=True))

    print(category_names)
    
    for index, row in df.iterrows():
        id = row.get('id')
        product_name = row.get('name')
        product_price = row.get('price')
        product_is_active = row.get('is_active')
        category_name = row.get('category')

        skip = False
        row_error = {}
        category_obj = None  

        def val(field):
            value = row.get(field)
            if pd.isna(value):
                row_error[field] = 'Missing'
                return 'Missing'
            return value

        val_id = val('id')
        val_name = val('name')
        val_price = val('price')
        val_active = val('is_active')
        val_category = val('category')
        
               
        if not (isinstance(product_price, int) or isinstance(product_price, float)):
            try:
                product_price = float(product_price)
            except (ValueError, TypeError):
                skip = True
                val_price = 'provide int value'
        
        if val_active != 'Missing':
            val_active = bool(val_active)

        if val_category not in category_names and not pd.isna(val_category):
            val_category = 'invalid category'
            skip = True
        
        errors.append({
            'id': val_id,
            'name': val_name,
            'price': val_price,
            'is_active': val_active,
            'category': val_category
        })

    
        if val_name == 'Missing' or val_price == 'Missing':
            skip = True

        if val_category != 'Missing':
            try:
                category_obj = Category.objects.get(name=val_category)
            except Category.DoesNotExist:
                row_error['category'] = 'Missing'
                skip = True
        else:
            skip = True

        if skip:
            continue  

        product, created = Product.objects.get_or_create(
            name=val_name,
            defaults={
                'price': product_price,
                'is_active': product_is_active,
            }
        )

        if not created:
            product.price = product_price
            product.is_active = product_is_active
            product.save()

        if category_obj is not None:
            product.categories.set([category_obj])

    if errors:
        errors_df = pd.DataFrame(errors)
        errors_df.to_excel('error_log.xlsx', index=False)

    return JsonResponse({"message": "File uploaded successfully"})


@api_view(['GET'])
def test(request):
    storage = Storage.objects.all()
    
    temp = Storage.objects.get(file='products.xlsx')
    
    path = temp.file.path

    return JsonResponse({"message":"success","path":path})

