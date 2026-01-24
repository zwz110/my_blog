from django.urls import path
from . import views as blog_v

app_name='blog'
urlpatterns=[
    path('',blog_v.index,name='index'),
]
