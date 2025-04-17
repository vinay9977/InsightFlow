from django.urls import path, re_path
from .views import login_user, register_user, auth_user, logout_user, register
from django.contrib.auth import views as auth_views



urlpatterns = [
    path('login/',login_user,name='login'),
    path('register/',register_user,name='register'),
    path('auth/',auth_user,name='auth-user'),
    path('logout/user/',logout_user,name='logout_user'),
    path('register/user/',register,name='user_register'),

    # Password reset URLs
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(
             template_name='password_reset_form.html',
             email_template_name='password_reset_email.html',
             subject_template_name='password_reset_subject.txt'
         ),
         name='password_reset'),
    
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='password_reset_done.html'
         ),
         name='password_reset_done'),
    
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='password_reset_confirm.html'
         ),
         name='password_reset_confirm'),
    
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='password_reset_complete.html'
         ),
         name='password_reset_complete'),
]