from django.shortcuts import render, redirect
from .forms import UserRegisterForm,UserLoginForm,FindPasswordForm,ResetPasswordForm,ChangePasswordForm,ChangeEmailForm
from blog.forms import PostForm
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.http import HttpResponse,JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.db.models import Q
import random
import string
from django.core.cache import cache
from django.conf import settings

# 生成6位数字验证码
def generate_captcha():
    return ''.join(random.choices(string.digits,k=6))

# 存储验证码到缓存，有效期5分钟
def store_captcha(email,captcha):
    cache.set(f'find_password:{email}',captcha,timeout=300)

# 验证验证码
def verify_captcha(email,captcha):
    cached_captcha=cache.get(f'find_password:{email}')
    if cached_captcha and cached_captcha==captcha:
        return True
    return False


# Create your views here.
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('blog:index')
    else:
        form = UserRegisterForm()
    return render(request, 'html/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())
            return redirect('blog:index')
        else:
            messages.error(request, '用户名或密码错误')
            return render(request,'html/login.html',{'form':form})
        
    else:
        form = UserLoginForm()
        return render(request, 'html/login.html', {'form': form})
def find_password(request):
    form=FindPasswordForm(request.POST or None)
    if request.method=='POST':
        if form.is_valid():
            user=form.user
            captcha=form.cleaned_data.get('captcha')
            if verify_captcha(user.email,captcha):
                request.session['reset_user_id']=user.id
                return redirect('user:reset_password',user_id=user.id)
            else:
                messages.error(request,'验证码错误或已过期')
                return render(request,'html/find_password.html',{'form':form})
        return render(request,'html/find_password.html',{'form':form})
    else:
        return render(request,'html/find_password.html',{'form':form})

@require_http_methods(['POST'])
def get_captcha(request):
    #获取验证码视图
    if request.method=='POST':
        username_or_email=request.POST.get('username_or_email')
        try:
            if not User.objects.filter(Q(username=username_or_email)|Q(email=username_or_email)):
                return JsonResponse({'success': False, 'message': '该用户名或邮箱不存在'})
            if User.objects.filter(username=username_or_email).exists():
                user=User.objects.get(username=username_or_email)
            else:
                user=User.objects.get(email=username_or_email)
            captcha=generate_captcha()
            store_captcha(user.email,captcha)

            # 发送邮件
            send_mail(
                subject='ZwZ Blog密码找回',
                message=f'您的密码找回验证码是：{captcha},有效期5分钟',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
            return JsonResponse({'success':True,'message':'验证码已发送'})
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'message': '该用户名或邮箱不存在'})
        # 捕获其他所有系统异常，返回通用友好提示（不暴露具体错误）
        except Exception as e:
            return JsonResponse({'success': False, 'message': '验证码发送失败，请稍后重试'})
    return JsonResponse({'success': False, 'message': '无效的请求'})
@require_http_methods(['POST'])
def send_register_captcha(request):
    #注册时发送验证码
    if request.method=='POST':
        # 尝试从JSON数据中获取邮箱
        import json
        try:
            data = json.loads(request.body)
            email = data.get('email')
            username=data.get('username')
        except json.JSONDecodeError:
            # 如果不是JSON格式，尝试从表单数据中获取
            email=request.POST.get('email')
            username=request.POST.get('username')
        
        if not email:
            return JsonResponse({'success': False, 'message': '请输入邮箱地址'})
        
        #检查邮箱是否已被注册
        if User.objects.filter(email=email).exists():
            return JsonResponse({'success': False, 'message': '该邮箱已被注册'})
        if User.objects.filter(username=username).exists():
            return JsonResponse({'success': False, 'message': '该用户名已被注册'})
        
        #生成并发送验证码
        captcha=generate_captcha()
        store_captcha(email,captcha)
        
        try:
            send_mail(
                subject='ZwZ Blog注册验证码',
                message=f'您的注册验证码是：{captcha},有效期5分钟',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
            return JsonResponse({'success':True,'message':'验证码已发送'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'发送失败：{str(e)}'})
    return JsonResponse({'success': False, 'message': '无效的请求'})
    


def reset_password(request, user_id):
    #重置密码视图
    session_user_id=request.session.get('reset_user_id')
    if not session_user_id or session_user_id != user_id:
        messages.error(request, '请先验证身份')
        return redirect('user:find_password')
    try:
        user=User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, '该用户不存在,请先注册账号')
        return redirect('user:register')
    #处理表单提交
    if request.method=='POST':
        form=ResetPasswordForm(request.POST)
        if form.is_valid():
            password=form.cleaned_data.get('password1')
            user.set_password(password)
            user.save()
            # 清除session，避免重复使用
            del request.session['reset_user_id']
            messages.success(request,'密码重置成功,请重新登录')
            return redirect('user:login')
    else:
        form=ResetPasswordForm()
    return render(request,'html/reset_password.html',{'form':form})
def logout(request):
    # 退出登录视图
    if request.method == 'POST':
        auth_logout(request)
        messages.success(request, '已退出登录')
        return redirect('user:login')
    else:
        form = UserLoginForm()
        return render(request, 'html/login.html', {'form': form})

def profile(request):
    # 个人中心视图
    if not request.user.is_authenticated:
        messages.error(request, '请先登录')
        return redirect('user:login')
    
    # 获取用户的文章，按创建时间倒序排列
    from blog.models import Post
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    
    posts_list = Post.objects.filter(author=request.user).order_by('-created_at')
    
    # 分页
    paginator = Paginator(posts_list, 3)  # 每页3篇文章
    page = request.GET.get('page')
    
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        # 如果page不是整数，显示第一页
        posts = paginator.page(1)
    except EmptyPage:
        # 如果page超出范围，显示最后一页
        posts = paginator.page(paginator.num_pages)

    return render(request, 'html/profile.html', {'posts': posts})
def my_posts(request):
    # 我的文章视图
    if not request.user.is_authenticated:
        messages.error(request, '请先登录')
        return redirect('user:login')
    
    # 获取用户的文章，按创建时间倒序排列
    from blog.models import Post
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    
    posts_list = Post.objects.filter(author=request.user).order_by('-created_at')
    
    # 分页
    paginator = Paginator(posts_list, 5)  # 每页5篇文章
    page = request.GET.get('page')
    
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        # 如果page不是整数，显示第一页
        posts = paginator.page(1)
    except EmptyPage:
        # 如果page超出范围，显示最后一页
        posts = paginator.page(paginator.num_pages)

    return render(request, 'html/my_posts.html', {'posts': posts})

def create_post(request):
    # 创建文章视图
    if not request.user.is_authenticated:
        messages.error(request, '请先登录')
        return redirect('user:login')
    
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            # 保存标签
            form.save_m2m()
            messages.success(request, '文章创建成功')
            return redirect('user:my_posts')
    else:
        form = PostForm()
    
    return render(request, 'html/create_post.html', {'form': form})

def edit_post(request, post_id):
    # 编辑文章视图
    if not request.user.is_authenticated:
        messages.error(request, '请先登录')
        return redirect('user:login')
    
    try:
        from blog.models import Post
        post = Post.objects.get(id=post_id, author=request.user)
    except Post.DoesNotExist:
        messages.error(request, '文章不存在或无权编辑')
        return redirect('user:my_posts')
    
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, '文章更新成功')
            return redirect('user:my_posts')
    else:
        form = PostForm(instance=post)
    
    return render(request, 'html/edit_post.html', {'form': form, 'post': post})

@require_http_methods(['POST'])
def delete_post(request):
    # 删除文章视图
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': '请先登录'})
    
    post_id = request.POST.get('post_id')
    if not post_id:
        return JsonResponse({'success': False, 'message': '缺少文章ID'})
    
    try:
        from blog.models import Post
        post = Post.objects.get(id=post_id, author=request.user)
        post.delete()
        return JsonResponse({'success': True, 'message': '文章删除成功'})
    except Post.DoesNotExist:
        return JsonResponse({'success': False, 'message': '文章不存在或无权删除'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'删除失败：{str(e)}'})

def my_comments(request):
    # 我的评论视图
    if not request.user.is_authenticated:
        messages.error(request, '请先登录')
        return redirect('user:login')
    
    # 获取用户的评论，按创建时间倒序排列
    from blog.models import Comment
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    
    comments_list = Comment.objects.filter(author=request.user).order_by('-created_at')
    
    # 分页
    paginator = Paginator(comments_list, 5)  # 每页5条评论
    page = request.GET.get('page')
    
    try:
        comments = paginator.page(page)
    except PageNotAnInteger:
        # 如果page不是整数，显示第一页
        comments = paginator.page(1)
    except EmptyPage:
        # 如果page超出范围，显示最后一页
        comments = paginator.page(paginator.num_pages)

    return render(request, 'html/my_comments.html', {'comments': comments})

@require_http_methods(['GET'])
def filter_comments(request):
    # 筛选评论视图
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': '请先登录'})
    
    # 获取筛选状态
    status = request.GET.get('status', 'all')
    
    # 获取用户的评论
    from blog.models import Comment
    comments_query = Comment.objects.filter(author=request.user)
    
    # 根据状态筛选
    if status != 'all':
        comments_query = comments_query.filter(status=status)
    
    # 按创建时间倒序排列
    comments_query = comments_query.order_by('-created_at')
    
    # 构建返回数据
    comments_data = []
    for comment in comments_query:
        try:
            # 获取文章URL
            post_url = comment.post.get_absolute_url()
        except:
            post_url = '#'
        
        # 构建状态样式和文本
        status_class = ''
        status_text = ''
        if comment.status == 'approved':
            status_class = 'bg-success'
            status_text = '已批准'
        elif comment.status == 'pending':
            status_class = 'bg-warning text-dark'
            status_text = '待审核'
        elif comment.status == 'spam':
            status_class = 'bg-danger'
            status_text = '垃圾评论'
        
        comments_data.append({
            'id': comment.id,
            'content': comment.content,
            'post_title': comment.post.title,
            'post_url': post_url,
            'status': comment.status,
            'status_class': status_class,
            'status_text': status_text,
            'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M'),
            'is_reply': comment.is_reply()
        })
    
    return JsonResponse({'success': True, 'comments': comments_data})

@require_http_methods(['POST'])
def delete_comment(request, comment_id):
    # 删除评论视图
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': '请先登录'})
    
    if not comment_id:
        return JsonResponse({'success': False, 'message': '缺少评论ID'})
    
    try:
        from blog.models import Comment
        comment = Comment.objects.get(id=comment_id, author=request.user)
        comment.delete()
        return JsonResponse({'success': True, 'message': '评论删除成功'})
    except Comment.DoesNotExist:
        return JsonResponse({'success': False, 'message': '评论不存在或无权删除'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'删除失败：{str(e)}'})

def my_favorites(request):
    # 我的收藏视图
    if not request.user.is_authenticated:
        messages.error(request, '请先登录')
        return redirect('user:login')
    
    # 获取用户的收藏，按收藏时间倒序排列
    from blog.models import Favorite
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    
    favorites_list = Favorite.objects.filter(user=request.user).order_by('-created_at')
    
    # 分页
    paginator = Paginator(favorites_list, 5)  # 每页5条收藏
    page = request.GET.get('page')
    
    try:
        favorites = paginator.page(page)
    except PageNotAnInteger:
        # 如果page不是整数，显示第一页
        favorites = paginator.page(1)
    except EmptyPage:
        # 如果page超出范围，显示最后一页
        favorites = paginator.page(paginator.num_pages)

    return render(request, 'html/my_favorites.html', {'favorites': favorites})

@require_http_methods(['POST'])
def delete_favorite(request, favorite_id):
    # 取消收藏视图
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': '请先登录'})
    
    if not favorite_id:
        return JsonResponse({'success': False, 'message': '缺少收藏ID'})
    
    try:
        from blog.models import Favorite
        favorite = Favorite.objects.get(id=favorite_id, user=request.user)
        favorite.delete()
        return JsonResponse({'success': True, 'message': '取消收藏成功'})
    except Favorite.DoesNotExist:
        return JsonResponse({'success': False, 'message': '收藏不存在或无权取消'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'取消收藏失败：{str(e)}'})

def account_settings(request):
    # 账号设置视图
    if not request.user.is_authenticated:
        messages.error(request, '请先登录')
        return redirect('user:login')
    
    password_form = ChangePasswordForm(user=request.user)
    email_form = ChangeEmailForm(user=request.user)
    
    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        
        if form_type == 'change_password':
            password_form = ChangePasswordForm(user=request.user, data=request.POST)
            if password_form.is_valid():
                password_form.save()
                messages.success(request, '密码修改成功，请重新登录')
                return redirect('user:login')
        
        elif form_type == 'change_email':
            email_form = ChangeEmailForm(user=request.user, data=request.POST)
            if email_form.is_valid():
                new_email = email_form.cleaned_data.get('new_email')
                request.user.email = new_email
                request.user.save()
                messages.success(request, '邮箱修改成功')
                return redirect('user:account_settings')
    
    return render(request, 'html/account_settings.html', {
        'password_form': password_form,
        'email_form': email_form
    })
