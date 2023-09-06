from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from .views import SignUpView

app_name = 'users'

urlpatterns = [
    path('sign_up/', SignUpView.as_view(), name='sign_up'),
    path('logged_out/', LogoutView.as_view(template_name='users/logged_out.html'), name='logout'),
    path('login/', LoginView.as_view(template_name='users/login.html'),
         name='login'),
]
