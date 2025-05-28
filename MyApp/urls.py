
from django.urls import path
from . import views

urlpatterns = [
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
    path('products/', views.ProductListCreateAPIView.as_view()),
    path('products/<int:id>/', views.ProductDetailAPIView.as_view()),
]