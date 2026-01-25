from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from taggit.managers import TaggableManager

# Create your models here.
class Post(models.Model):
    """文章模型"""
    # 文章状态选项
    STATUS_CHOICES = (
        ('published', '已发布'),
        ('draft', '草稿'),
    )
    
    # 文章分类选项
    CATEGORY_CHOICES = (
        ('技术分享', '技术分享'),
        ('生活随笔', '生活随笔'),
        ('学习笔记', '学习笔记'),
        ('项目经验', '项目经验'),
    )
    
    title = models.CharField(max_length=200, verbose_name='标题')
    slug = models.SlugField(max_length=200, unique_for_date='published_at', verbose_name='slug')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts', verbose_name='作者')
    content = models.TextField(verbose_name='内容')
    summary = models.CharField(max_length=500, blank=True, verbose_name='摘要')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='技术分享', verbose_name='分类')
    tags = TaggableManager(blank=True, verbose_name='标签')
    feature_image = models.ImageField(upload_to='post_images/', blank=True, null=True, verbose_name='特色图片')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft', verbose_name='状态')
    published_at = models.DateTimeField(default=timezone.now, verbose_name='发布时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '文章'
        verbose_name_plural = '文章'
        ordering = ('-published_at',)
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('blog:post_detail', kwargs={
            'year': self.published_at.year,
            'month':self.published_at.month,  # 1 → "01"
            'day': self.published_at.day,  # 5 → "05"
            'slug': self.slug
        })
    def save(self, *args, **kwargs):
        # 自动生成 slug：如果为空，用标题生成
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

class Comment(models.Model):
    """评论模型"""
    # 评论状态选项
    STATUS_CHOICES = (
        ('approved', '已批准'),
        ('pending', '待审核'),
        ('spam', '垃圾评论'),
    )
    
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments', verbose_name='文章')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments', verbose_name='作者')
    content = models.TextField(verbose_name='内容')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies', verbose_name='父评论')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending', verbose_name='状态')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '评论'
        verbose_name_plural = '评论'
        ordering = ('created_at',)
    
    def __str__(self):
        return f'评论 by {self.author.username} on {self.post.title}'
    
    def is_reply(self):
        return self.parent is not None

class Message(models.Model):
    """留言模型"""
    name = models.CharField(max_length=50, verbose_name='姓名')
    email = models.EmailField(max_length=100, verbose_name='邮箱')
    content = models.TextField(verbose_name='留言内容')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    status = models.CharField(
        max_length=20,
        choices=(('pending', '待审核'), ('approved', '已批准'), ('rejected', '已拒绝')),
        default='pending',
        verbose_name='状态'
    )

    class Meta:
        verbose_name = '留言'
        verbose_name_plural = '留言管理'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name}: {self.content[:30]}'
