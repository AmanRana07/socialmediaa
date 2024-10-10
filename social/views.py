from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import login, authenticate
from django.contrib import messages
from .forms import LoginForm, RegisterForm, PostForm, ProfileForm
from django.contrib.auth.decorators import login_required
from .models import Post, Profile


@login_required
def index(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(
                commit=False
            )  # Create post instance but don't save to DB yet
            post.user = (
                request.user
            )  # Associate the post with the currently logged-in user
            post.save()  # Now save the post
            return redirect("index")  # Redirect to the index page after saving
        else:
            print(form.errors)  # Print errors for debugging
    else:
        form = PostForm()

    # Fetch all posts to display them on the index page
    user_profile = get_object_or_404(Profile, user=request.user)
    posts = Post.objects.filter(user=request.user)  # Fetch posts for the logged-in user
    profile_picture = request.user.profile.profile_picture.url
    all_users = Profile.objects.exclude(user=request.user)
    followed_users = user_profile.followers.all()
    return render(
        request,
        "social/index.html",
        {
            "form": form,
            "posts": posts,
            "profile_picture": profile_picture,
            "all_users": all_users,
            "user_profile": user_profile,
        },
    )


def login_view(request):
    if request.user.is_authenticated:
        return redirect("index")

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("index")
            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = LoginForm()
    return render(request, "social/auth/login.html", {"form": form})


def register_view(request):
    if request.user.is_authenticated:
        return redirect("index")  # Redirect if already logged in

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # login(request, user)  # Automatically log the user in after registration
            messages.success(request, "Registration successful.")
            return redirect("login")
        else:
            messages.error(request, "Please correct the error below.")
    else:
        form = RegisterForm()
    return render(request, "social/auth/register.html", {"form": form})


def profile_view(request):
    if request.user.is_authenticated:
        # Fetch posts for the logged-in user
        posts = Post.objects.filter(user=request.user)
        profile_picture = (
            request.user.profile.profile_picture.url
        )  # Filter posts by user
    else:
        posts = Post.objects.none()  # No posts if user is not authenticated

    return render(
        request,
        "social/profile.html",
        {"posts": posts, "profile_picture": profile_picture},
    )  # Pass posts to the template


@login_required
def edit_post(request, post_id):
    post = get_object_or_404(
        Post, id=post_id, user=request.user
    )  # Ensure user owns the post
    if request.method == "POST":
        form = PostForm(
            request.POST, request.FILES, instance=post
        )  # Populate form with existing post data
        if form.is_valid():
            form.save()  # Save the updated post
            return redirect("profile")  # Redirect to profile page after saving
    else:
        form = PostForm(instance=post)  # Load form with existing post data
    return render(request, "social/edit_post.html", {"form": form})


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(
        Post, id=post_id, user=request.user
    )  # Ensure user owns the post
    if request.method == "POST":
        post.delete()  # Delete the post
        return redirect("profile")  # Redirect to profile page after deletion
    return render(request, "social/delete_post_confirm.html", {"post": post})


@login_required
def profile_edit(request):
    # Get or create the profile instance for the logged-in user
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect("profile")  # Redirect to the profile page after saving
    else:
        form = ProfileForm(instance=profile)

    return render(
        request,
        "social/profile_edit.html",
        {"form": form, "profile": profile},
    )


@login_required
def follow_user(request, user_id):
    user_to_follow = get_object_or_404(Profile, id=user_id)
    if request.user in user_to_follow.followers.all():
        user_to_follow.followers.remove(request.user)
        messages.success(request, f"You unfollowed {user_to_follow.user.username}.")
    else:
        user_to_follow.followers.add(request.user)
        messages.success(
            request, f"You are now following {user_to_follow.user.username}."
        )
    return redirect("index")


@login_required
def update_profile(request):
    profile = request.user.profile

    if request.method == "POST":
        if "profile_picture" in request.FILES:
            profile.profile_picture = request.FILES["profile_picture"]
        if "bio" in request.POST:
            profile.bio = request.POST["bio"]
        profile.save()
        return redirect("your_redirect_url")  # Redirect after the update

    return render(request, "your_template.html", {"profile": profile})
