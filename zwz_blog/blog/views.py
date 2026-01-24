from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request,'blog/index.html')

def about(request):
    return render(request,'html/about.html')

def category(request):
    return render(request,'html/category.html')
def tag(request):
    return render(request,'html/tag.html')
def create_post(request):
    return render(request,'html/create_post.html')
