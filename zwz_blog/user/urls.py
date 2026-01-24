from django.urls import path
from . import views

app_name = 'user'
urlpatterns = [
    path('register/', views.register, name='register'),
    path('send_register_captcha/', views.send_register_captcha, name='send_register_captcha'),
    path('login/', views.user_login, name='login'),
    path('find_password/', views.find_password, name='find_password'),
    path('reset_password/<int:user_id>/', views.reset_password, name='reset_password'),
    path('find_password/get_captcha/', views.get_captcha, name='get_captcha'),
]

