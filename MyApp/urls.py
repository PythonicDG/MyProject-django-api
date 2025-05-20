
from django.urls import path
from .views import login_api_view, logout_api_view, current_user_api_view


urlpatterns = [
    path('login/', login_api_view, name = 'login'),
    path('logout/',logout_api_view, name = 'logout'),
    path('current_user/', current_user_api_view, name = 'current_user'),
]