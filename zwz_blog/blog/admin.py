from django.contrib import admin
from .models import Message, Comment

# 注册留言模型到后台管理
@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'content', 'status', 'created_at')
    list_editable = ('status',)  # 允许在列表页面直接编辑状态
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'email', 'content')
    ordering = ('-created_at',)
    fields = ('name', 'email', 'content', 'status', 'created_at')  # 确保详情页面显示所有字段
    readonly_fields = ('created_at',)  # 创建时间只读

# 注册评论模型到后台管理
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'post', 'content', 'status', 'is_reply', 'created_at')
    list_editable = ('status',)  # 允许在列表页面直接编辑状态
    list_filter = ('status', 'created_at')
    search_fields = ('author__username', 'post__title', 'content')
    ordering = ('-created_at',)
    fields = ('author', 'post', 'content', 'parent', 'status', 'created_at')
    readonly_fields = ('author', 'post', 'parent', 'created_at')  # 这些字段只读
    
    def is_reply(self, obj):
        """判断是否为回复"""
        return obj.is_reply()
    is_reply.boolean = True  # 显示为布尔值图标
    is_reply.short_description = '是否为回复'

