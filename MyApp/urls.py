
from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name ='login'),
    path('logout/',views.logout_view, name='logout'),
    path('get_user/', views.get_user, name='get_user'),
    path('registration/', views.registration, name='registration'),
    path('verify_otp/', views.verify_otp, name='verify_otp'),
    path('get_group_info/', views.get_group_info, name='get_group_info'),
]