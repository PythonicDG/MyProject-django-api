
from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, CategoryViewSet
from .views import OrderViewSet
from django.views.generic import TemplateView
from django.urls import re_path
from django.views.generic import RedirectView

router = DefaultRouter()

router.register(r'categories', CategoryViewSet)
router.register(r'products', ProductViewSet)
router.register(r'orders', views.OrderViewSet)

urlpatterns = [
    path('', RedirectView.as_view(url='/admin/', permanent=False)),
    path('login/', views.login_view, name ='login'),
    path('logout/',views.logout_view, name='logout'),
    path('get_user/', views.get_user, name='get_user'),
    path('registration/', views.registration, name='registration'),
    path('verify_otp/', views.verify_otp, name='verify_otp'),
    path('register_email/', views.register_email, name='register_email'),
    path('fetch_groups/', views.fetch_groups, name='fetch_groups'),
    path('delete_user/<str:username>/', views.delete_user, name='delete_user'),
    path('get_users/',views.get_users, name='get_users'),
    path('update_user/<str:username>/', views.update_user, name='update_user'),
    #class based
    path('cart/', views.CartListCreateAPIView.as_view()),
    path('cart/<int:id>/', views.CartDetailAPIView.as_view()),
    
    path('',include(router.urls)),
    path('testing/', views.preview_email, name='preview_email'),

    #order and payment
    path('place_order/', views.place_order, name='place_order'),
    path('make_payment/', views.make_payment, name='make_payment'),
    path('update_order_status/', views.update_order_status, name='update_order_status'),
    path('remove_item/', views.remove_item, name='remove_item'),
    path('cancel_order/', views.cancel_order, name='cancel_order'),
    path('get_orders/', views.get_orders, name='get_orders'),

    #excel file upload and download and processing  
    path('download_excel/', views.download_excel, name='download_excel'),
    path('upload_excel/', views.upload_excel, name='upload_excel'),
    #testing
    path('test/', views.test, name='test'),
    
    path('send_notification/', views.send_notification),
    path('get_token/', TemplateView.as_view(template_name='get_token.html')),
        re_path(r'^firebase-messaging-sw.js$', TemplateView.as_view(
        template_name="firebase-messaging-sw.js",
        content_type='application/javascript'
    )),


    

]