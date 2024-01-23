from django.urls import path
from . import views

app_name = 'comment'


urlpatterns = [
    # 发表评论
    path('post-comment/<int:article_id>/', views.PostCommentView.as_view(), name='post_comment'),
    # 处理二级回复
    path('post-comment/<int:article_id>/<int:parent_comment_id>/', views.PostCommentView.as_view(), name='comment_reply')
]