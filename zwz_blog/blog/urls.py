from django.urls import path
from . import views as blog_v

app_name='blog'
urlpatterns=[
    path('',blog_v.index,name='index'),
    path('about/',blog_v.about,name='about'),
    path('category/',blog_v.category,name='category'),
    path('category/<str:category_name>/',blog_v.category,name='category_detail'),
    path('tag/',blog_v.tag,name='tag'),
    path('tag/<str:tag_name>/',blog_v.tag,name='tag_detail'),
    path('<int:year>/<int:month>/<int:day>/<slug:slug>/',blog_v.post_detail,name='post_detail'),
    path('search/',blog_v.search,name='search')
]
