from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse

from django.views.decorators.cache import cache_page

from .forms import CommentForm, PostForm
from .models import Comment, Follow, Group, Post


User = get_user_model()


POSTS_PER_PAGE = 12

def index(request):
    post_list = Post.objects.select_related('group')
    paginator = Paginator(post_list, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'index.html', {'page': page, 'paginator': paginator})


def group_posts(request, slug):
    """Функция возвращает страницу сообщества
    и выводит до 12 записей на странице.
    """
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    posts_quantity = paginator.count
    return render(request, 'group.html', {
        'posts_quantity': posts_quantity,
        'group': group, 
        'posts': posts, 
        'page': page, 
        'paginator': paginator})


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = author.posts.all()
    paginator = Paginator(post_list, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    posts_quantity = paginator.count
    following = False
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            user=request.user,
            author=author).exists()
    followers = Follow.objects.filter(author=author).count()
    follows = Follow.objects.filter(user=author).count()
    return render(request, 'profile.html', {
        'posts_quantity': posts_quantity,
        'page': page, 
        'author': author, 
        'paginator': paginator,
        'following': following,
        'followers': followers,
        'follows': follows})


def post_view(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    comments = Comment.objects.filter(post_id=post_id)
    form = CommentForm(request.POST or None)
    posts_quantity = post.author.posts.all().count
    following = False
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            user=request.user,
            author=post.author).exists()
    followers = Follow.objects.filter(author=post.author).count()
    follows = Follow.objects.filter(user=post.author).count()
    return render(request, 'post.html', {
        'form': form, 
        'author': post.author, 
        'post': post,
        'posts_quantity': posts_quantity,
        'comments': comments,
        'following': following, 
        'followers': followers,
        'follows': follows})


@login_required
def new_post(request):
    form = PostForm(request.POST or None,
    files=request.FILES or None)
    if request.method == 'GET' or not form.is_valid():
        return render(request, 'new.html', {'form': form, 'is_edit': False})
    post = form.save(commit=False)
    post.author = request.user
    form.save()
    return redirect(reverse('index'))


@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    author = post.author
    if request.user != author:
        return redirect(reverse('index'))
    form = PostForm(request.POST or None, 
    files=request.FILES or None, 
    instance=post)
    if request.method == 'GET' or not form.is_valid():
        return render(request, 'new.html', {
            'form': form, 
            'is_edit': True, 
            'post': post})
    post = form.save(commit=False)
    form.save()
    return redirect(reverse('post', kwargs={
            'username': username, 
            'post_id': post_id, 
            }))


def page_not_found(request, exception=None):
    return render(
        request, 
        'misc/404.html', 
        {'path': request.path}, 
        status=404
    )


def server_error(request):
    return render(request, 'misc/500.html', status=500)


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    form = CommentForm(request.POST or None)
    context = {
        'post': post,
        'form': form
    }
    if not form.is_valid():
        return render(request, 'includes/comments.html', context)
    comment = form.save(commit=False)
    comment.author = request.user
    comment.post = post
    form.save()
    return redirect(reverse('post', kwargs={
            'username': username, 
            'post_id': post_id, 
            }))


@login_required
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(post_list, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'follow.html', {
        'page': page, 
        'paginator': paginator})


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user != author and not Follow.objects.filter(
        user=request.user, author=author).exists():
        Follow.objects.create(user=request.user, author=author)
    return profile(request, username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(user=request.user, author=author).delete()
    return profile(request, username)
