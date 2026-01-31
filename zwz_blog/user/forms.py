from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django import forms
from django.contrib.auth.models import User
from django.db.models import Q

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text='请输入您的邮箱地址')
    captcha = forms.CharField(
        label='验证码',
        max_length=6,
        min_length=6,  # 强制6位，避免用户输入位数不对
        required=True,
        help_text='请输入6位数字验证码'
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

# 添加登录表单
class UserLoginForm(AuthenticationForm):
    pass

class FindPasswordForm(forms.Form):
    username_or_email=forms.CharField(label='用户名或邮箱')
    captcha=forms.CharField(label='验证码',max_length=6)
    def clean_username_or_email(self):
        value=self.cleaned_data.get('username_or_email')
        if not User.objects.filter(Q(username__exact=value)|Q(email__exact=value)):
            raise forms.ValidationError('用户名或邮箱不存在')
        self._user_value=value
        return value
    @property
    def user(self):
        if not hasattr(self,'_user_value'):
            raise ValueError('请先调用 form.is_valid() 验证表单')
        return User.objects.get(Q(username__exact=self._user_value)|Q(email__exact=self._user_value))

class ResetPasswordForm(forms.Form):
    password1=forms.CharField(label='新密码',widget=forms.PasswordInput)
    password2=forms.CharField(label='确认新密码',widget=forms.PasswordInput)
    def clean_password2(self):
        password1=self.cleaned_data.get('password1')
        password2=self.cleaned_data.get('password2')
        if password1 and password2:
            if password1!=password2:
                raise forms.ValidationError('两次输入密码不一致')
        return password2

class ChangePasswordForm(forms.Form):
    old_password=forms.CharField(label='当前密码',widget=forms.PasswordInput)
    new_password1=forms.CharField(label='新密码',widget=forms.PasswordInput)
    new_password2=forms.CharField(label='确认新密码',widget=forms.PasswordInput)
    def __init__(self,user,*args,**kwargs):
        self.user=user
        super().__init__(*args,**kwargs)
    def clean_old_password(self):
        old_password=self.cleaned_data.get('old_password')
        if not self.user.check_password(old_password):
            raise forms.ValidationError('当前密码错误')
        return old_password
    def clean_new_password2(self):
        new_password1=self.cleaned_data.get('new_password1')
        new_password2=self.cleaned_data.get('new_password2')
        if new_password1 and new_password2:
            if new_password1!=new_password2:
                raise forms.ValidationError('两次输入的新密码不一致')
        return new_password2
    def save(self):
        password=self.cleaned_data.get('new_password1')
        self.user.set_password(password)
        self.user.save()

class ChangeEmailForm(forms.Form):
    new_email=forms.EmailField(label='新邮箱地址')
    password=forms.CharField(label='当前密码',widget=forms.PasswordInput)
    def __init__(self,user,*args,**kwargs):
        self.user=user
        super().__init__(*args,**kwargs)
    def clean_password(self):
        password=self.cleaned_data.get('password')
        if not self.user.check_password(password):
            raise forms.ValidationError('当前密码错误')
        return password
    def clean_new_email(self):
        new_email=self.cleaned_data.get('new_email')
        if User.objects.filter(email=new_email).exists():
            raise forms.ValidationError('该邮箱已被注册')
        return new_email
