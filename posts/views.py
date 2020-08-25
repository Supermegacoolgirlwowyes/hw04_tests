from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm
from .models import Group, Post, User


def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {'page': page, 'paginator': paginator}
    return render(request, 'index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {'group': group, 'page': page, 'paginator': paginator}
    return render(request, 'group.html', context)


@login_required
def new_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            form.instance.author = request.user
            form.save()
            return redirect('index')
    else:
        form = PostForm()
    return render(request, 'posts/new.html', {'form': form})


def profile(request, username):
    username = User.objects.get(username=username)
    user_posts = Post.objects.filter(author=username)
    posts_count = Post.objects.filter(author=username).count()
    paginator = Paginator(user_posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'username': username,
        'user_posts': user_posts,
        'posts_count': posts_count,
        'page': page,
        'paginator': paginator
    }
    return render(request, 'profile.html', context)


def post_view(request, username, post_id):
    username = User.objects.get(username=username)
    post = Post.objects.get(author=username, id=post_id)
    posts_count = Post.objects.filter(author=username).count()
    context = {
        'username': username,
        'post': post,
        'posts_count': posts_count,
    }
    return render(request, 'post.html', context)


@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = PostForm(request.POST or None, instance=post)
    if post.author != request.user:
        return redirect('post', username=username, post_id=post_id)
    if request.method == 'POST':
        if form.is_valid():
            form.instance.id = post_id
            form.save()
            return redirect('post', username=username, post_id=post_id)
    return render(request, 'posts/new.html', {'form': form, 'post': post})
