from django.urls import path
from . import views

app_name = 'user'
urlpatterns = [
    path('register/', views.register, name='register'),
    path('send_register_captcha/', views.send_register_captcha, name='send_register_captcha'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('find_password/', views.find_password, name='find_password'),
    path('reset_password/<int:user_id>/', views.reset_password, name='reset_password'),
    path('find_password/get_captcha/', views.get_captcha, name='get_captcha'),
    path('myposts/',views.my_posts,name='my_posts'),
    path('createposts/',views.create_post,name='create_post'),
    path('edit_post/<int:post_id>/',views.edit_post,name='edit_post'),
    path('delete_post/<int:post_id>/',views.delete_post,name='delete_post'),
    path('my_comments/',views.my_comments,name='my_comments'),
    path('filter_comments/',views.filter_comments,name='filter_comments'),
    path('delete_comment/<int:comment_id>/',views.delete_comment,name='delete_comment'),
    path('my_favorites/',views.my_favorites,name='my_favorites'),
    path('delete_favorite/<int:favorite_id>/',views.delete_favorite,name='delete_favorite'),
    path('account_settings/',views.account_settings,name='account_settings'),
]