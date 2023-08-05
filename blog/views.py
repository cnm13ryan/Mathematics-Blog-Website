from django.shortcuts import redirect, render, get_object_or_404
from .models import Author, Category, Post, Comment, Reply
from .utils import update_views
from .forms import PostForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.exceptions import MultipleObjectsReturned


def home(request):
    forums = Category.objects.all()
    num_posts = Post.objects.all().count()
    num_users = User.objects.all().count()
    num_categories = forums.count()
    try:
        last_post = Post.objects.latest("date")
    except:
        last_post = []

    context = {
        "forums":forums,
        "num_posts":num_posts,
        "num_users":num_users,
        "num_categories":num_categories,
        "last_post":last_post,
        "title": "MATH forum app"
    }
    return render(request, "blog/forums.html", context)

def detail(request, slug):
    try:
        post = get_object_or_404(Post, slug=slug)
        profile_pic_url = post.user.profile_pic.url if post.user.profile_pic and post.user.profile_pic.name else None  # Updated linek
    
        if request.user.is_authenticated:
            try:
                author = Author.objects.get(user=request.user)
            except Author.DoesNotExist:
                author = None  # or handle the exception in some other way 
    
        if "comment-form" in request.POST:
            comment = request.POST.get("comment")
            new_comment, created = Comment.objects.get_or_create(user=author, content=comment)
            post.comments.add(new_comment.id)

        if "reply-form" in request.POST:
            reply = request.POST.get("reply")
            commenr_id = request.POST.get("comment-id")
            comment_obj = Comment.objects.get(id=commenr_id)
            new_reply, created = Reply.objects.get_or_create(user=author, content=reply)
            comment_obj.replies.add(new_reply.id)


        context = {
            "post":post,
            'profile_pic_url': profile_pic_url,
            "title": "MATH: "+post.title,
        }

        update_views(request, post)

        return render(request, "blog/detail.html", context)

    except Post.DoesNotExist:
        # handle the case where the post does not exist
        return render(request, '404.html', status=404)

    except MultipleObjectsReturned:
        # handle the case where multiple posts are returned
        posts = Post.objects.filter(slug=slug)
        # Here you can decide what to do when multiple posts are returned.
        # For example, you can return the first post:
        post = posts.first()
        profile_pic_url = post.user.profile_pic.url if post.user.profile_pic and post.user.profile_pic.name else None  # Updated line
        context = {
            "post":post,
            'profile_pic_url': profile_pic_url,
            "title": "MATH: "+post.title,
        }

        update_views(request, post)

        return render(request, "blog/detail.html", context)

def posts(request, slug):
    category = get_object_or_404(Category, slug=slug)
    posts = Post.objects.filter(approved=True, categories=category)
    paginator = Paginator(posts, 5)
    page = request.GET.get("page")
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages) 

    context = {
        "posts":posts,
        "forum": category,
        "title": "MATH: Posts"
    }

    return render(request, "blog/posts.html", context)


@login_required
def create_post(request):
    context = {}
    form = PostForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            print("\n\n its valid")
            author, created = Author.objects.get_or_create(user=request.user)
            new_post = form.save(commit=False)
            new_post.user = author
            new_post.save()
            form.save_m2m()
            return redirect("home")
    context.update({
        "form": form,
        "title": "MATH: Create New Post"
    })
    return render(request, "blog/create_post.html", context)

def latest_posts(request):
    posts = Post.objects.all().filter(approved=True)[:10]
    context = {
        "posts":posts,
        "title": "MATH: Latest 10 Posts"
    }

    return render(request, "blog/latest-posts.html", context)

def search_result(request):

    return render(request, "blog/search.html")
