# I wrote this code

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from .models import *
from .forms import *

# Ensure the user is logged in to access this view.
# This decorator is used across all views that require login.
@login_required
def profile(request, username):
    # Fetch the user based on the username or return a 404 if not found.
    user = get_object_or_404(User, username=username)
    # Fetch the latest 3 status and image posts by the user.
    status_posts = StatusPost.objects.filter(user=user).order_by('-created_at')[:3]
    image_posts = ImagePost.objects.filter(user=user).order_by('-uploaded_at')[:3]
    # Initialize the image upload form
    image_form = ImageUploadForm()
    # Get 5 random friends or all of them if less than 5.
    friends = user.profile.friends.all().order_by('?')[:5]
    # Fetch pending friend requests.
    pending_requests = FriendRequest.objects.filter(recipient=request.user.profile, status=FriendRequest.STATUS_PENDING)

    # Aggregate a context to be passed to the template.
    context = {
        'user_profile': user.profile,           # The UserProfile instance
        'friends': friends,                     # List of 5 or less friends
        'is_friend': request.user.profile in user.profile.friends.all(), # Check if the logged-in user is a friend
        'statuses': status_posts,               # User's status posts
        'images': image_posts,                  # User's image posts
        'image_form': image_form,               # Image upload form
        'pending_requests': pending_requests,   # Pending friend requests for the logged in user
    }

    #  Render the profile template with all the data
    return render(request, 'social_app/profile.html', context)

class CustomLoginView(LoginView):
    form_class = CustomAuthenticationForm

    def get_success_url(self):
        success_url = reverse('profile', args=[self.request.user.username])
        return success_url

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('profile', username=request.user.username)
        return super().dispatch(request, *args, **kwargs)

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'You have successfully registered! Please log in!')
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def edit_profile(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save(user=request.user)
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile', username=request.user.username)
    else:
        # Get the first and last name from the User model.
        initial_data = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
        }
        # Populate the form with the UserProfile fields plus the first and last name.
        form = UserProfileForm(instance=request.user.profile, initial=initial_data)

    return render(request, 'social_app/edit_profile.html', {'form': form})

@login_required
def send_friend_request(request, user_id):
    recipient = get_object_or_404(User, id=user_id)

    # Get the referrer URL
    referrer_url = request.META.get('HTTP_REFERER', None)

    if FriendRequest.objects.filter(sender=request.user.profile, recipient=recipient.profile).exists() or FriendRequest.objects.filter(sender=recipient.profile, recipient=request.user.profile).exists():
        messages.error(request, "One of you has already requested friendship!")
        # Redirect to the referrer URL or default to the profile page.
        if referrer_url:
            return redirect(referrer_url)
        else:
            return redirect('profile', username=request.user.username)

    FriendRequest.objects.create(sender=request.user.profile, recipient=recipient.profile)
    messages.success(request, f"Friend request sent to {recipient.username}!")

    # Redirect to the referrer URL or default to the profile page.
    if referrer_url:
        return redirect(referrer_url)
    else:
        return redirect('profile', username=request.user.username)

@login_required
def accept_friend_request(request, request_id):
    friend_request = get_object_or_404(FriendRequest, id=request_id, recipient=request.user.profile)
    friend_request.accept()
    messages.success(request, f"You are now friends with {friend_request.sender.user.username}!")
    return redirect('profile', friend_request.recipient.user.username)

@login_required
def decline_friend_request(request, request_id):
    friend_request = get_object_or_404(FriendRequest, id=request_id, recipient=request.user.profile)
    friend_request.decline()
    messages.info(request, "Friend request declined.")
    return redirect('profile', friend_request.recipient.user.username)

@login_required
def unfriend(request, friend_id):
    friend_profile = get_object_or_404(UserProfile, id=friend_id)
    if friend_profile in request.user.profile.friends.all():
        request.user.profile.friends.remove(friend_profile)
        FriendRequest.objects.filter(sender=request.user.profile, recipient=friend_profile, status=FriendRequest.STATUS_ACCEPTED).delete()
        FriendRequest.objects.filter(sender=friend_profile, recipient=request.user.profile, status=FriendRequest.STATUS_ACCEPTED).delete()
        messages.success(request, f"You have unfriended {friend_profile.user.username}.")
    else:
        messages.error(request, f"You are not friends with {friend_profile.user.username}.")
    return redirect('profile', request.user.username)

@login_required
def all_friends(request, username):
    user = get_object_or_404(User, username=username)
    friends = user.profile.friends.all()
    context = {
        'friends': friends,
        'user_profile': user  # The user whose friends are being displayed.
    }
    return render(request, 'social_app/all_friends.html', context)

@login_required
def search_results(request):
    # Fetch all friends of the logged-in user.
    friends = request.user.profile.friends.all()
    # Get the search query from the request.
    query = request.GET.get('search_query')
    results = []
    if query:
        # Filter users based on the search query but exclude the user with the username "admin".
        results = User.objects.filter(username__icontains=query).exclude(username="admin")
    return render(request, 'social_app/search_results.html', {'results': results, 'friends': friends})

@login_required
def all_posts(request, username):
    user = get_object_or_404(User, username=username)
    statuses = StatusPost.objects.filter(user=user).order_by('-created_at')
    context = {
        'statuses': statuses,
        'user_profile': user  # The user whose posts are being displayed.
    }
    return render(request, 'social_app/all_posts.html', context)

@login_required
def post_status(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == 'POST':
        form = StatusPostForm(request.POST)
        if form.is_valid():
            status = form.save(commit=False)
            status.user = request.user
            status.save()
            # Redirect back to user's home page.
            return redirect('profile', username=request.user.username)
    else:
        form = StatusPostForm()
    return render(request, 'social_app/post_status.html', {'form': form})

@login_required
def like_status(request, status_id):
    if not request.user.is_authenticated:
        return redirect('login')

    status = get_object_or_404(StatusPost, id=status_id)
    
    # Check if the user has already liked this post.
    already_liked = Like.objects.filter(user=request.user, post=status).exists()
    if already_liked:
        Like.objects.filter(user=request.user, post=status).delete()
        messages.success(request, 'You unliked the post.')
    else:
        Like.objects.create(user=request.user, post=status)
        messages.success(request, 'You liked a post.')

    # Get the referrer URL (where the user comes from).
    referrer_url = request.META.get('HTTP_REFERER', None)
    return redirect(referrer_url)

@login_required
def add_comment(request, status_id):
    if not request.user.is_authenticated:
        return redirect('login')

    status = get_object_or_404(StatusPost, id=status_id)
    content = request.POST.get('content')
    Comment.objects.create(user=request.user, post=status, content=content)
    messages.success(request, 'Comment added successfully.')

    # Get the referrer URL (where the user comes from).
    referrer_url = request.META.get('HTTP_REFERER', None)
    return redirect(referrer_url)

@login_required
def chat_room(request, room_id):
    try:
        room = ChatRoom.objects.get(id=room_id)

        # Check if the user is one of the friends associated with the chat.
        if request.user not in [room.user1, room.user2]:
            messages.error(request, "You do not have permission to access this chat.")
            return redirect(request.META.get('HTTP_REFERER', '/'))
        
        # Determine the friend's username.
        if request.user == room.user1:
            friend_username = room.user2.username
        else:
            friend_username = room.user1.username

        chat_messages_list = room.chat_messages.order_by('-timestamp')[:20]
        return render(request, 'social_app/chat_room.html', {
            'room_id': room_id,
            'chat_messages': chat_messages_list,
            'friend_username': friend_username
        })
    except ChatRoom.DoesNotExist:
        messages.error(request, "No such chat exists.")
        return redirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def start_chat(request, friend_id):
    friend = get_object_or_404(User, id=friend_id)
    
    # Check if a chat room already exists between the two users.
    chat_room = ChatRoom.objects.filter(
        (Q(user1=request.user) & Q(user2=friend)) | 
        (Q(user1=friend) & Q(user2=request.user))
    ).first()

    # If no chat room exists, create one.
    if not chat_room:
        chat_room = ChatRoom.objects.create(user1=request.user, user2=friend)

    return redirect('chat_room', room_id=chat_room.id)

@login_required
def all_messages(request):
    user = request.user

    # Query the ChatRoom model for chat rooms where the user is either user1 or user2.
    chatrooms = ChatRoom.objects.filter(Q(user1=user) | Q(user2=user))
    friends_with_chat_history = []

    # Create a list of chat rooms with the other user's name and the chat room's ID.
    for chatroom in chatrooms:
        if chatroom.user1 == user:
            friend = chatroom.user2.profile
        else:
            friend = chatroom.user1.profile
        friends_with_chat_history.append(friend)

    return render(request, 'social_app/messages.html', {'friends_with_chat_history': friends_with_chat_history})

@login_required
def upload_image(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            image_post = form.save(commit=False)
            image_post.user = request.user
            image_post.save()
            messages.success(request, 'Image uploaded successfully!')
            return redirect(request.META.get('HTTP_REFERER', None))
    else:
        form = ImageUploadForm()
    return redirect(request.META.get('HTTP_REFERER', None))

@login_required
def all_images(request, username):
    user = get_object_or_404(User, username=username)
    images = ImagePost.objects.filter(user=user).order_by('-uploaded_at')
    context = {
        'images': images,
        'user_profile': user  # The user whose image posts are being displayed.
    }
    return render(request, 'social_app/all_images.html', context)

# end of code I wrote