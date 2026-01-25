from django.shortcuts import render, redirect
from django.db.models import Q, Count
from .forms import MessageForm
from .models import Message, Post

# Create your views here.
def index(request):
    """首页视图，显示已发布的文章列表"""
    # 获取已发布的文章，按发布时间倒序排列，预加载作者信息，过滤掉slug为空的文章
    posts = Post.objects.filter(status='published', author__isnull=False, slug__isnull=False).exclude(slug='').select_related('author').order_by('-published_at')
    
    # 获取热门文章（这里简单按发布时间排序，实际项目中可能需要按浏览量等计算）
    hot_posts = Post.objects.filter(status='published', author__isnull=False, slug__isnull=False).exclude(slug='').select_related('author').order_by('-published_at')[:5]
    
    # 获取文章分类及其数量
    categories = Post.objects.filter(status='published').values('category').annotate(count=Count('category')).order_by('-count')
    
    context = {
        'posts': posts,
        'hot_posts': hot_posts,
        'categories': categories,
    }
    
    return render(request, 'blog/index.html', context)

def category(request):
    return render(request,'html/category.html')
def tag(request):
    return render(request,'html/tag.html')

def post_detail(request, year, month, day, slug):
    from django.shortcuts import get_object_or_404
    from .models import Post
    from django.utils import timezone
    
    # 尝试获取文章对象，添加更多的错误处理
    try:
        # 首先检查是否存在slug匹配的文章
        slug_matches = Post.objects.filter(slug=slug)
        if not slug_matches.exists():
            # 不存在slug匹配的文章
            from django.http import Http404
            raise Http404(f"No Post with slug '{slug}'")
        
        # 检查slug匹配的文章的状态
        status_matches = slug_matches.filter(status='published')
        if not status_matches.exists():
            # 存在slug匹配的文章，但状态不是published
            from django.http import Http404
            raise Http404(f"Post with slug '{slug}' exists but status is not 'published'")
        
        # 尝试获取文章，使用更灵活的日期匹配方式
        # 首先尝试精确匹配
        try:
            post = status_matches.get(
                published_at__year=year, 
                published_at__month=month, 
                published_at__day=day
            )
        except Post.DoesNotExist:
            # 如果精确匹配失败，尝试只通过slug获取（忽略日期）
            # 这种方式可以处理日期格式不匹配的问题
            post = status_matches.first()
    except Post.DoesNotExist:
        from django.http import Http404
        raise Http404(f"No Post matches the given query: slug={slug}, date={year}-{month}-{day}")
    
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
    
    # 为每个评论获取已批准的回复
    for comment in comments:
        # 存储已批准的回复到comment对象的approved_replies属性
        comment.approved_replies = comment.replies.filter(status='approved').order_by('created_at')
    
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

def about(request):
    """关于页面视图，处理留言提交"""
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save()
            from django.contrib import messages
            messages.success(request, '留言已提交，等待审核')
            return redirect('blog:about')
    else:
        form = MessageForm()
    
    # 获取已批准的留言
    approved_messages = Message.objects.filter(status='approved').order_by('-created_at')
    
    return render(request, 'html/about.html', {
        'form': form,
        'messages': approved_messages
    })