from django.db import models

# Create your models here.
# 导入内建的User模型
from django.contrib.auth.models import User
from django.urls import reverse
# 导入timezone处理与时间相关的事物
from django.utils import timezone
from taggit.managers import TaggableManager
from PIL import Image



class AriticleColumn(models.Model):
    """
        栏目的 Model
    """

    # 栏目标题
    title = models.CharField(max_length=100, blank=True)
    # 创建时间
    created =  models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title

# 博客文章数据模型：作者、标题、正文、创建时间、修改时间
class ArticlePost(models.Model):
    # 文章作者。参数 on_delete 用于指定数据删除的方式
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    # 文章标题。models.CharField 为字符串字段，用于保存较短的字符串，比如标题
    title = models.CharField(max_length=100)
    # 文章正文。保存大量文本使用 TextField
    body = models.TextField()
    # 文章创建时间。参数 default=timezone.now 指定其在创建数据时将默认写入当前的时间
    created = models.DateTimeField(default=timezone.now)
    # 文章更新时间。参数 auto_now=True 指定每次数据更新时自动写入当前时间
    updated = models.DateTimeField(auto_now=True)
    # 浏览量
    total_views = models.PositiveIntegerField(default=0)
    # 文章栏目
    column = models.ForeignKey(AriticleColumn, null=True, blank=True, on_delete=models.CASCADE, related_name='article')
    # 文章标签
    tags = TaggableManager(blank=True)
    # 文章标题图
    avatar = models.ImageField(upload_to='article/%Y%m%d', blank=True)
    # 保存时处理照片
    def save(self, *args, **kwargs):
        # 调用原来的save()功能
        article = super(ArticlePost, self).save(*args, **kwargs)

        # 固定宽度缩放图片大小,这样做的目的是避免用户进入文章详情页面时重复处理已经缩放和保存过的图片
        if self.avatar and not kwargs.get('update_fields'):
            image = Image.open(self.avatar)
            (width, height) = image.size
            new_width = 400
            new_height = int(new_width * (height / width))
            resized_image = image.resize((new_width, new_height), Image.ANTIALIAS)
            resized_image.save(self.avatar.path)

        return article
    # 内部类，给models定义元数据
    class Meta:
        # ordering 指定模型返回的数据的排列顺序
        # '-created' 表明数据应该以倒序排列
        ordering = ('-created',)

    # __str__定义当调用对象的str()方法时的返回值
    def __str__(self):
        # 返回文章标题
        return self.title

        # 获取文章地址
    def get_absolute_url(self):
        return reverse('article:article_detail', args=[self.id])
