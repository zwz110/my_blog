from django.shortcuts import render, redirect
from django.db.models import Q

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
    comments = post.comments.filter(status='published').order_by('created_at')
    
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
def search(request):
    # 导入模型
    from .models import Post
    
    # 1. 规范化关键词：去除首尾空格，统一处理空值
    query = request.GET.get('search', '').strip()
    posts = Post.objects.none()  # 初始化空查询集
    
    if query:
        try:
            # 2. 优化查询：只查询需要的字段，减少数据库负载
            #    增加索引友好的查询条件（status='published' 前置）
            posts = Post.objects.filter(
                Q(status='published') & 
                (Q(title__icontains=query) | Q(content__icontains=query) | Q(tags__name__icontains=query))
            ).distinct().select_related('author')  # 预加载关联字段，减少N+1查询
            
            # 3. 可选：添加排序，让搜索结果更有意义
            posts = posts.order_by('-published_at')
            
            # 4. 为每个帖子计算已批准的评论数量
            for post in posts:
                post.approved_comments_count = post.comments.filter(status='approved').count()
            
        except Exception as e:
            # 4. 异常处理：捕获数据库查询异常，避免程序崩溃
            print(f"搜索出错: {str(e)}")  # 实际项目中建议用logger记录
            posts = Post.objects.none()
    
    # 5. 传递更多上下文，方便模板展示
    context = {
        'posts': posts,
        'query': query,
        'total_results': posts.count(),  # 告诉用户搜索结果数量
    }
    return render(request, 'html/search.html', context)