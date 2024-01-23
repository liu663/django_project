# 引入redirect重定向模块
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
# 引入HttpResponse
from django.http import HttpResponse
from django.template.backends import django
from taggit.models import Tag
from taggit.utils import parse_tags

# 引入刚才定义的ArticlePostForm表单类
from .forms import ArticlePostForm
# 引入User模型
from django.contrib.auth.models import User
from .models import ArticlePost
import markdown
# 引入分页模块
from django.core.paginator import Paginator
# 引入 Q 对象
from django.db.models import Q
from comment.models import Comment
from comment.forms import CommentForm
# 引入栏目Modle
from .models import AriticleColumn



# 视图函数
def article_list(request):
    search = request.GET.get('search')
    order = request.GET.get('order')
    column = request.GET.get('column')
    tag = request.GET.get('tag')
    # 初始化查询集
    article_list = ArticlePost.objects.all()
    # 搜索查询集
    if search:
        article_list = article_list.filter(
            Q(title__icontains=search) |
            Q(body__icontains=search)
        )
    else:
        search = ''

    # 栏目查询集
    if column is not None and column.isdigit():
        article_list = article_list.filter(column=column)

    # 标签查询集
    if tag and tag != 'None':
        article_list = article_list.filter(tags__name__in=[tag])

    # 查询集排序
    if order == 'total_views':
        article_list = article_list.order_by('-total_views')
    # 每页显示一篇文章
    paginator = Paginator(article_list, 3)
    page = request.GET.get('page')
    # 将导航对象相应的页码内容返回给 articles
    articles = paginator.get_page(page)
    # 需要传递给模板（templates）的对象
    context = {'articles': articles, 'order': order, 'search': search, 'column': column, 'tag': tag}
    # render函数：载入模板，并返回context对象
    return render(request, 'article/list.html', context)


# 文章详情
def article_detail(request, id):
    # 取出相应的文章
    article = ArticlePost.objects.get(id=id)
    # 引入评论表单
    comment_form = CommentForm()
    # 取出文章评论
    comments = Comment.objects.filter(article=id)
    # 需要传递给模板的对象,context字典的键主要用于标识存储在其中的值的特定数据。
    # <h1>{{ article.title }}</h1>
    # <p>{{ article.content }}</p>

    # 浏览量 +1
    article.total_views += 1
    article.save(update_fields=['total_views'])
    # 将markdown语法渲染成html样式
    md = markdown.Markdown(extensions=[
                                         # 包含 缩写、表格等常用扩展
                                         'markdown.extensions.extra',
                                         # 语法高亮扩展
                                         'markdown.extensions.codehilite',
                                         'markdown.extensions.toc',
                                     ])
    article.body = md.convert(article.body)
    context = {'article': article, 'toc': md.toc, 'comments': comments, 'comment_form': comment_form}
    # 载入模板，并返回context对象
    return render(request, 'article/detail.html', context)


# 写文章的视图
# 检查登录
@login_required(login_url='/userprofile/login/')
def article_create(request):
    # 判断用户是否提交数据
    if request.method == 'POST':
        # 将提交的数据赋值到表单实例中
        article_post_form = ArticlePostForm(request.POST, request.FILES)
        # 判断提交的数据是否满足模型的要求
        if article_post_form.is_valid():
            # 保存数据，但暂时不提交到数据库中
            new_article = article_post_form.save(commit=False)
            # 指定数据库中 id=1 的用户为作者
            # 如果你进行过删除数据表的操作，可能会找不到id=1的用户
            # 此时请重新创建用户，并传入此用户的id
            new_article.author = User.objects.get(id=request.user.id)
            if request.POST['column'] != 'none':
                new_article.column = AriticleColumn.objects.get(id=request.POST['column'])
            # 将新文章保存到数据库中
            new_article.save()
            # 保存文章的多对多关系
            article_post_form.save_m2m()
            # 完成后返回到文章列表
            return redirect("article:article_list")
        # 如果数据不合法，返回错误信息
        else:
            return HttpResponse("表单内容有误，请重新填写。")
    # 如果用户请求获取数据
    else:
        # 创建表单类实例
        article_post_form = ArticlePostForm()
        columns = AriticleColumn.objects.all()
        # 赋值上下文
        context = {'article_post_form': article_post_form, 'columns': columns}
        # 返回模板
        return render(request, 'article/create.html', context)


# 安全删除文章
@login_required(login_url='/userprofile/login/')
def article_safe_delete(request, id):
    if request.method == 'POST':
        article = ArticlePost.objects.get(id=id)
        if article.author == request.user:
            article.delete()
            return redirect("article:article_list")
        else:
            return HttpResponse("无权限执行此操作")
    else:
        return HttpResponse("仅允许post请求")


# 更新文章
@login_required(login_url='/userprofile/login/')
def article_update(request, id):
    """
    更新文章的视图函数
    通过POST方法提交表单，更新titile、body字段
    GET方法进入初始表单页面
    id： 文章的 id
    """
    # 获取需要修改的具体的文章对象
    article = ArticlePost.objects.get(id=id)

    # 检查当前登录用户是否是文章的作者
    if article.author != request.user:
        return HttpResponse("无权限执行此操作")

    # 判断用户是否为POST提交表单数据
    if request.method == "POST":
        # 将提交的数据赋值到表单实例中
        article_post_form = ArticlePostForm(data=request.POST)
        # 判断提交的数据是否满足模型的要求
        if article_post_form.is_valid():
            # 从请求中获取标签数据
            if request.FILES.get('avatar'):
                article.avatar = request.FILES.get('avatar')

            tag_names = request.POST.getlist('tags')

            # 清除原有的标签
            article.tags.clear()

            # 解析并关联每个标签名称
            for tag_name in tag_names:
                tags = parse_tags(tag_name)
                for tag in tags:
                    article.tags.add(tag)
            # 保存新写入的title、body数据并保存
            article.title = request.POST['title']
            article.body = request.POST['body']
            if request.POST['column'] != 'none':
                article.column = AriticleColumn.objects.get(id=request.POST['column'])
            else:
                article.column = None
            article.save()
            # 保存文章的多对多关系
            # article_post_form.save_m2m()
            # 完成后返回到修改的文章中。徐传入文章的id值
            return redirect("article:article_detail", id=id)
        # 如果数据不合法，返回错误信息
        else:
            return HttpResponse("表单内容有误，请重新填写。")
    # 如果用户GET请求获取数据
    else:
        # 创建表单数据
        article_post_form = ArticlePostForm()
        columns = AriticleColumn.objects.all()
        # 赋值上下文，将article文章对象也传递进去，以便提取旧的内容
        context = {'article': article, 'article_post_form': article_post_form, 'columns': columns}
        # 将响应返回到模板中
        return render(request, 'article/update.html', context)
