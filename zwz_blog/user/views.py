from django.shortcuts import render, redirect
from .forms import UserRegisterForm,UserLoginForm,FindPasswordForm,ResetPasswordForm
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

