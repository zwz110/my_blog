from django import forms
from .models import Post,Message
from taggit.forms import TagField, TagWidget

class PostForm(forms.ModelForm):
    """文章表单"""
    tags = TagField(widget=TagWidget(attrs={'placeholder': '请输入标签，多个标签用逗号分隔'}), required=False)
    
    class Meta:
        model = Post
        fields = ['title', 'content', 'summary', 'category', 'tags', 'feature_image', 'status', 'published_at']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': '请输入文章标题'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 10, 'placeholder': '请输入文章内容'}),
            'summary': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': '请输入文章摘要'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'published_at': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'feature_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'title': '文章标题',
            'content': '文章内容',
            'summary': '文章摘要',
            'category': '文章分类',
            'tags': '文章标签',
            'feature_image': '特色图片',
            'status': '文章状态',
            'published_at': '发布时间',
        }

class MessageForm(forms.ModelForm):
    """留言表单"""
    class Meta:
        model = Message
        fields = ['name', 'email', 'content']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入您的姓名'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': '请输入您的邮箱'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': '请输入您的留言内容'}),
        }
