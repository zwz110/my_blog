# ZwZ Blog

一个基于Django的个人博客系统，功能完整，界面美观。

## 功能特性

- **用户管理**
  - 注册、登录、退出
  - 密码找回
  - 个人中心
  - 账号设置（修改密码、修改邮箱）

- **文章管理**
  - 创建、编辑、删除文章
  - 文章分类和标签
  - 文章详情页
  - 文章搜索

- **评论系统**
  - 发表评论
  - 评论回复
  - 评论审核

- **收藏功能**
  - 文章收藏/取消收藏
  - 我的收藏页面

- **其他功能**
  - 留言板
  - 分类和标签页面
  - 响应式设计

## 技术栈

- **后端**：Django 4.x
- **前端**：HTML5, CSS3, JavaScript
- **CSS框架**：Bootstrap 5
- **图标库**：Font Awesome
- **数据库**：SQLite (默认)
- **其他**：django-taggit (标签管理)

## 安装步骤

### 1. 克隆项

```bash
git clone <repository-url>
cd ZwZ-Blog
```

### 2. 创建虚拟环境

```bash
# Windows
python -m venv venv

# Linux/Mac
python3 -m venv venv
```

### 3. 激活虚拟环境

```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 4. 安装依赖

```bash
pip install -r requirements.txt
```

### 5. 配置数据库

```bash
# 生成迁移文件
python manage.py makemigrations

# 执行迁移
python manage.py migrate
```

### 6. 创建超级用户

```bash
python manage.py createsuperuser
```

### 7. 运行开发服务器

```bash
python manage.py runserver
```

访问 http://127.0.0.1:8000/ 即可查看网站。

## 项目结构

```
ZwZ-Blog/
├── manage.py
├── requirements.txt
├── zwz_blog/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   ├── asgi.py
│   ├── blog/
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── forms.py
│   │   ├── templates/
│   │   │   └── blog/
│   │   │       └── post_detail.html
│   │   └── urls.py
│   ├── user/
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── forms.py
│   │   └── urls.py
│   └── templates/
│       └── html/
│           ├── base.html
│           ├── index.html
│           ├── profile.html
│           ├── my_posts.html
│           ├── my_comments.html
│           ├── my_favorites.html
│           ├── account_settings.html
│           ├── register.html
│           ├── login.html
│           ├── find_password.html
│           ├── reset_password.html
│           ├── category.html
│           ├── category_detail.html
│           ├── tag.html
│           ├── tag_detail.html
│           ├── search.html
│           └── about.html
```

## 使用说明

### 1. 管理后台

访问 http://127.0.0.1:8000/admin/ 登录后台管理系统，可以管理用户、文章、评论、留言等。

### 2. 前台功能

- **首页**：展示最新文章
- **分类**：按分类查看文章
- **标签**：按标签查看文章
- **关于**：网站介绍和留言板
- **搜索**：搜索文章
- **个人中心**：管理个人文章、评论、收藏
- **账号设置**：修改个人信息和密码

### 3. 文章管理

登录后，点击导航栏的用户名，在下拉菜单中选择"我的文章"，可以查看、创建、编辑和删除自己的文章。

### 4. 评论管理

在个人中心的"我的评论"页面，可以查看自己的评论和回复。

### 5. 收藏管理

在个人中心的"我的收藏"页面，可以查看和管理自己收藏的文章。

## 配置说明

### 邮件配置

在 `zwz_blog/settings.py` 中配置邮件服务器，用于发送密码找回验证码：

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.qq.com'  # 邮件服务器
EMAIL_PORT = 587  # 端口
EMAIL_USE_TLS = True  # 使用TLS
EMAIL_HOST_USER = 'your_email@qq.com'  # 邮箱地址
EMAIL_HOST_PASSWORD = 'your_email_password'  # 邮箱密码或授权码
DEFAULT_FROM_EMAIL = 'your_email@qq.com'  # 默认发件人
```

### 媒体文件配置

在 `zwz_blog/settings.py` 中配置媒体文件存储路径：

```python
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request 来改进这个项目。

## 作者

ZwZ

---

如果您觉得这个项目不错，欢迎给个 Star！