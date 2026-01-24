from django.db import models

# Create your models here.
# 注意：不要在这里定义User类，Django已经内置了完整的User模型
# 如有需要，可以创建用户扩展模型

# class UserProfile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     avatar = models.ImageField(upload_to='avatars/', blank=True)
#     bio = models.TextField(max_length=500, blank=True)
#     website = models.URLField(blank=True)
#
#     def __str__(self):
#         return f"{self.user.username}'s profile"
