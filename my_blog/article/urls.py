from django.urls import path
from . import views

# 正在部署的应用的名称
app_name = 'article'

urlpatterns = [
    # 当用户请求article/article-list链接时，会调用views.py中的article_list函数，
    # 并返回渲染后的对象。参数name用于反查url地址，相当于给url起了个名字，以后会用到
    path('article-list/', views.article_list, name='article_list'),
    # 文章详情
    # 其中<int:id>部分是一个动态路径参数，用于接受一个整数类型的值作为文章的ID
    path('article-detail/<int:id>/', views.article_detail, name='article_detail'),
    # 写文章
    path('article-create/', views.article_create, name='article_create'),
    # 删除文章
    path('article-safe-delete/<int:id>/', views.article_safe_delete, name='article_safe_delete'),
    # 更新文章
    path('article-update/<int:id>/', views.article_update, name="article_update"),
]
