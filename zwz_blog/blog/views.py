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

def post_detail(request, year, month, day, slug):
    from django.shortcuts import get_object_or_404
    from .models import Post
    from django.utils import timezone
    
    # 获取文章对象
    post = get_object_or_404(Post, slug=slug, 
                           published_at__year=year, 
                           published_at__month=month, 
                           published_at__day=day, 
                           status='published')
    
    # 处理评论提交
    if request.method == 'POST' and request.user.is_authenticated:
        from .models import Comment
        content = request.POST.get('content')
        if content:
            comment = Comment.objects.create(
                post=post,
                author=request.user,
                content=content,
                status='pending'
            )
            from django.contrib import messages
            messages.success(request, '评论已提交，等待审核')
            return redirect('blog:post_detail', year=year, month=month, day=day, slug=slug)
    
    # 获取已批准的评论
    comments = post.comments.filter(status='approved').order_by('created_at')
    
    # 获取相关文章
    related_posts = Post.objects.filter(
        category=post.category,
        status='published'
    ).exclude(id=post.id)[:4]
    
    return render(request, 'blog/post_detail.html', {
        'post': post,
        'comments': comments,
        'related_posts': related_posts
    })
