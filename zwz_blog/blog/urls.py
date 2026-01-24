from django.urls import path
from . import views as blog_v

app_name='blog'
urlpatterns=[
    path('',blog_v.index,name='index'),
    path('about/',blog_v.about,name='about'),
    path('category/',blog_v.category,name='category'),
    path('tag/',blog_v.tag,name='tag'),
    path('creatpost/',blog_v.create_post,name='create_post')
]
