from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .forms import RegistrationForm, LoginForm, CommentForm, MessageForm
from django.contrib.auth.decorators import login_required
from .models import Post, Category, Message, Comment, Likes, Notification, User, Profile
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.utils import timezone
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.contrib.auth.tokens import default_token_generator
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect
from django.http import JsonResponse


User = get_user_model()  # Use the default User model

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()  # Save the form and get the user object
            # Get the raw password for authentication
            raw_password = form.cleaned_data.get('password1')  # 'password1' if using UserCreationForm
            # Authenticate the user with the provided credentials
            authenticated_user = authenticate(username=user.username, password=raw_password)
            if authenticated_user is not None:
                login(request, authenticated_user)
                messages.success(request, f'Welcome, {user.username}!')
                return redirect('nourse:complete')
        else:
            # If the form is not valid, re-render the registration page with the form and errors
            return render(request, 'register.html', {'form': form})        
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})

def verify_email(request, token):
    user = get_object_or_404(User, verification_token=token)
    user.is_active = True
    user.email_verified = True
    user.verification_token = ''
    user.save()
    return redirect('email_verified')

@login_required
def complete_profile(request):
    if request.method == 'POST':
        title = request.POST.get('title', '')
        picture = request.FILES.get('picture')  # Use FILES to handle file uploads
        bio = request.POST.get('bio', '')
        work_field = request.POST.get('work_field', '')

        profile = request.user.profile
        if picture:
            profile.picture = picture  # Save the uploaded profile picture
        profile.title = title
        profile.bio = bio
        profile.work_field = work_field
        profile.save()

        return redirect('nourse:profile')  # Change 'profile' to the actual name of your profile view URL

    return render(request, 'complete_profile.html')

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome, {username}!')
                return redirect('nourse:home')  # Adjust to your home URL pattern
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

@login_required  
def main(request):
    category_id = request.GET.get('category')
    if category_id:
        posts = Post.objects.filter(category_id=category_id)
    else:
        posts = Post.objects.all()
    
    categories = Category.objects.all()
    
    user_picture = request.user.profile.picture.url if request.user.is_authenticated and request.user.profile.picture else None
    
    return render(request, 'main.html', {
        'posts': posts,
        'categories': categories,
        'user_picture': user_picture
    })

@login_required
def create_post(request):
    categories = Category.objects.all()
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        category_id = request.POST.get('category')
        category = get_object_or_404(Category, id=category_id)
        
        post = Post(title=title, content=content, category=category, user=request.user)
        
        if request.FILES.get('picture'):
            post.image = request.FILES.get('picture')
        
        post.save()
        return redirect('nourse:profile')  # Adjust to your profile URL pattern
    
    return render(request, 'create_post.html', {'categories': categories})

@login_required
def profile(request):
    user = request.user
    profile = get_object_or_404(Profile, user=user)
    posts = Post.objects.filter(user=user).order_by('date_posted')
    categories = Category.objects.all()
    return render(request, 'profile.html', {'profile': profile, 'posts': posts, 'categories': categories})

def contact(request):
    return render(request, 'contact.html')

@login_required
def edit_profile(request):
    user = request.user
    categories = Category.objects.all()
    profile = get_object_or_404(Profile, user=user)

    if request.method == 'POST':
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        user.save()

        profile.bio = request.POST.get('bio')
        profile.work_field = request.POST.get('work_field')
        if request.FILES.get('picture'):
            # Delete the old picture if it exists
            if profile.picture:
                profile.picture.delete()
            profile.picture = request.FILES.get('picture')
        
        profile.save()

        messages.success(request, 'Profile updated successfully!')
        return redirect('nourse:profile')

    return render(request, 'edit_profile.html', {'user': user, 'profile': profile, 'categories': categories})

def posts_by_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    posts = Post.objects.filter(category=category)
    return render(request, 'create_post.html', {'posts': posts, 'category': category})

def category_view(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    posts = Post.objects.filter(category=category)
    categories = Category.objects.all()
    return render(request, 'category.html', {
        'category': category,
        'posts': posts,
        'categories': categories,
    })

def search_view(request):
    query = request.GET.get('q')  # Get the search query
    posts = Post.objects.all()  # Default to all posts
    users = User.objects.all()
    if query:
        posts = posts.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(user__username__icontains=query) |  # Search by username
            Q(category__name__icontains=query)  # Search by category name
        )
        users = users.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        )
    return render(request, 'search_results.html', {'posts': posts, 'users': users, 'query': query})

def index(request):
    posts = Post.objects.all()
    categories = Category.objects.all()
    return render(request, 'index.html', {'posts': posts, 'categories': categories})

@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.post = post
            comment.save()
            return redirect('nourse:post_detail', post_id=post.id)  # Adjust to your post detail URL pattern
    else:
        form = CommentForm()
    return render(request, 'add_comment.html', {'form': form})

@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    user = request.user

    if post.likes.filter(id=user.id).exists():
        post.likes.remove(user)
        Notification.objects.filter(user=post.user, post=post, message=f'{user.username} liked your post.').delete()
    else:
        post.likes.add(user)
        Notification.objects.create(user=post.user, post=post, message=f'{user.username} liked your post.')

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def send_message(request):
    if request.method == 'POST':
        content = request.POST.get('content')
        recipient_id = request.POST.get('recipient_id')
        
        if not content or not recipient_id:
            return redirect('nourse:inbox')  # Redirect back if form data is missing
        
        try:
            recipient = get_object_or_404(User, id=recipient_id)
        except User.DoesNotExist:
            return redirect('nourse:inbox')  # Redirect back if recipient does not exist
        
        Message.objects.create(
            sender=request.user,
            recipient=recipient,
            content=content,
            date_sent=timezone.now()
        )
        
        return redirect('nourse:inbox')  # Redirect back to inbox or another appropriate page

    return redirect('nourse:inbox')
    
@login_required
def inbox(request, recipient_id=None):
    if recipient_id:
        recipient = get_object_or_404(UserProfile, id=recipient_id)
        chat_messages = Message.objects.filter(
            sender__in=[request.user.profile, recipient],
            recipient__in=[request.user.profile, recipient]
        ).order_by('date_sent')
    else:
        recipient = None
        chat_messages = []

    received_messages = Message.objects.filter(recipient=request.user.profile).order_by('-date_sent')

    return render(request, 'inbox.html', {
        'chat_messages': chat_messages,
        'recipient': recipient,
        'received_messages': received_messages
    })

def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.all()
    return render(request, 'post_detail.html', {'post': post, 'comments': comments})

@login_required
def view_message(request, message_id):
    message = get_object_or_404(Message, id=message_id, receiver=request.user)
    return render(request, 'view_message.html', {'message': message})

@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Post deleted successfully!')
        return redirect('nourse:profile')  # Redirect to a suitable page
    return render(request, 'confirm_delete.html', {'post': post})

@login_required
def inbox(request, recipient_id=None):
    user = request.user
    
    # Retrieve all messages where the user is either the sender or recipient
    all_messages = Message.objects.filter(Q(sender=user) | Q(recipient=user)).order_by('date_sent')

    # Use a set to store unique user pairs as conversations
    conversations = {}
    for message in all_messages:
        other_party = message.sender if message.recipient == user else message.recipient
        if other_party in conversations:
            conversations[other_party].append(message)
        else:
            conversations[other_party] = [message]
    
    # Prepare the last message for each conversation
    received_messages = []
    for other_party, messages in conversations.items():
        last_message = messages[-1]
        received_messages.append((other_party, last_message))
    
    # If a specific recipient is selected, filter the messages for that conversation
    if recipient_id:
        recipient = get_object_or_404(User, id=recipient_id)
        chat_messages = all_messages.filter(Q(sender=recipient) | Q(recipient=recipient))
    else:
        recipient = None
        chat_messages = []

    context = {
        'received_messages': received_messages,
        'chat_messages': chat_messages,
        'recipient': recipient,
    }
    
    return render(request, 'inbox.html', context)

def search_users(request):
    username = request.GET.get('username', '')
    User = get_user_model()
    users = User.objects.filter(username__icontains=username).exclude(id=request.user.id)[:5]
    
    user_data = [{
        'id': user.id,
        'username': user.username,
        'full_name': f"{user.first_name} {user.last_name}",
        'picture_url': user.picture.url if user.picture else '/static/default_profile_pic.png'
    } for user in users]
    
    return JsonResponse(user_data, safe=False)

@login_required
def complete(request):
    user = request.user
    categories = Category.objects.all()
    
    if request.method == 'POST':
        form = CompleteProfileForm(request.POST, request.FILES, instance=user.profile)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = user
            profile.save()
            messages.success(request, 'Profile completed successfully!')
            return redirect('nourse:profile')
    else:
        form = CompleteProfileForm(instance=user.profile)
    
    return render(request, 'complete_profile.html', {'user': user, 'categories': categories, 'form': form})