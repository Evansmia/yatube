from django.core.paginator import Paginator
from .models import Group, Post, Follow
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from .forms import PostForm, CommentForm
from django.conf import settings

User = get_user_model()


def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, settings.POST_PAGING_COUNT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(
        request,
        'posts/index.html',
        {'page_obj': page_obj, }
    )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, settings.POST_PAGING_COUNT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(
        request,
        'posts/group_list.html',
        {'group': group,
         'page_obj': page_obj, }
    )


def profile(request, username):
    author = get_object_or_404(User, username=username)
    following = (
        request.user.is_authenticated
        and request.user.username != username
        and Follow.objects.filter(user=request.user, author=author).exists()
    )
    posts_author = Post.objects.filter(author_id=author.id)
    paginator = Paginator(posts_author, settings.POST_PAGING_COUNT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    number_of_posts = posts_author.count()
    return render(
        request,
        'posts/profile.html',
        {'author': author,
         'page_obj': page_obj,
         'posts_author': posts_author,
         'number_of_posts': number_of_posts,
         'following': following, }
    )


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    text = post.text
    return render(
        request,
        'posts/post_detail.html',
        {'post': post,
         'text': text,
         'form': form,
         'comments': post.comments.all(), }
    )


@login_required
def post_create(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if request.method == "POST":
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('posts:profile', username=post.author.username)
    return render(
        request,
        'posts/create_post.html',
        {'form': form, }
    )


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect('posts:post_detail', post_id=post_id)

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post_id)

    return render(
        request,
        'posts/create_post.html',
        {'form': form,
         'post': post,
         'edit': True, }
    )


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    posts = Post.objects.filter(
        author__following__user=request.user
    )
    paginator = Paginator(posts, settings.POST_PAGING_COUNT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj}
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    user = request.user
    author = get_object_or_404(User, username=username)
    if user != author:
        Follow.objects.get_or_create(
            user=user,
            author=author
        )
    return redirect('posts:follow_index')


@login_required
def profile_unfollow(request, username):
    get_object_or_404(
        Follow, user=request.user, author__username=username).delete()
    return redirect('posts:follow_index')
