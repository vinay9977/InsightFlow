from django.urls import path, re_path
from .views import login_user, register_user, auth_user, logout_user, register


urlpatterns = [
    path('login',login_user,name='login'),
    path('register',register_user,name='register'),
    path('auth',auth_user,name='auth-user'),
    path('logout/user',logout_user,name='logout_user'),
    path('register/user',register,name='user_register')
]