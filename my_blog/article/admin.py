from django.contrib import admin

# Register your models here.
# 需要“告诉”Django，后台中需要添加ArticlePost这个数据表供管理
# .models 表示当前目录下的 models.py 文件，而 ArticlePost 是在该文件中定义的模型类
from .models import ArticlePost, AriticleColumn

# 注册ArticlePost到admin中
admin.site.register(ArticlePost)
# 注册文章栏目
admin.site.register(AriticleColumn)
