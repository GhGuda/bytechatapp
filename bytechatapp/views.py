import json
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from .models import Message, CustomUser
from django.contrib.auth.models import auth
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.decorators import login_required
import re
from django.db.models import Q, Max


# Create your views here.
def index(request):
    if request.user.is_authenticated:
        return redirect(frontpage)
    else:
        if request.method == "POST":
            username_or_mail = request.POST['username']
            password = request.POST['password']
            auth_user = auth.authenticate(username=username_or_mail, password=password)
            
            try:
                if "@" in username_or_mail:
                    username = CustomUser.objects.filter(email=username_or_mail).first()
                    auth_user = auth.authenticate(username=username.username, password=password)
                    
                else:
                    auth_user = auth.authenticate(username=username_or_mail, password=password)

                if auth_user is not None:
                    auth.login(request, auth_user)
                    return redirect('frontpage')
                else:
                    messages.error(request, "Password or username not found.")
            
            except:
                messages.error(request, "Invalid email or password, retry")
                return redirect('index')
    return render(request, "index.html")




def logout(request):
    auth.logout(request)
    return redirect('index')


def register(request):
    if request.method == "POST":
        username = request.POST['username'].lower()
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']
        
        
        

        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            messages.error(request, "Username can only contain letters, numbers, and underscores!")
            return redirect('register')
        
        elif username.isdigit(): 
            messages.error(request, "Username cannot consist of only numbers!")
            return redirect('register')
        
        elif len(username) <= 0:
            messages.error(request, "Enter username!")
            return redirect('register')
        
        elif ' ' in username:
            messages.error(request, "Username cannot contain spaces, can only contain letters, numbers, and underscores!")
            return redirect('register')
        
        elif CustomUser.objects.filter(username__iexact=username).exists():
            messages.error(request, "Username taken!")
            return redirect('register')
        
        elif password == username:
            messages.error(request, "Password similar to username!")
            return redirect('register')
        
        elif len(email) <= 0:
            messages.error(request, "Enter email!")
            return redirect('register')
        
        elif len(password) < 8:
            messages.error(request, "Password is weak, enter strong password!")
            return redirect('register')
        
        elif CustomUser.objects.filter(email=email).exists():
            messages.error(request, "Email taken!")
            return redirect('register')
        elif password != password2:
            messages.error(request, "Password doesn't match")
            return redirect('register')            
        
        else:
            new_user = CustomUser.objects.create_user(username=username, email=email, password=password)
            new_user.save()
            auth_new_user = auth.authenticate(username=username, password=password)
            auth.login(request,auth_new_user)
            return redirect('frontpage')
    return render(request, "register.html")


def mark_users_offline():
    from django.utils import timezone
    from datetime import timedelta
    from .models import CustomUser

    threshold = timezone.now() - timedelta(minutes=3)
    CustomUser.objects.filter(last_seen__lt=threshold, is_online=True).update(is_online=False)



def frontpage(request):
    """Show chat list with last message + AJAX auto-refresh."""
    current_user = request.user
    if not current_user.is_authenticated:
        return JsonResponse({"error": "Unauthorized"}, status=403)

    # All messages involving current user
    all_msgs = Message.objects.filter(
        Q(sender=current_user) | Q(receiver=current_user)
    )

    # Find latest message per conversation pair
    latest_pairs = (
        all_msgs
        .values('sender', 'receiver')
        .annotate(latest_time=Max('timestamp'))
        .order_by('-latest_time')
    )

    contacts = []
    seen = set()

    for pair in latest_pairs:
        sender_id = pair['sender']
        receiver_id = pair['receiver']
        contact_id = receiver_id if sender_id == current_user.id else sender_id

        if contact_id in seen:
            continue

        try:
            contact_user = CustomUser.objects.get(id=contact_id)
        except CustomUser.DoesNotExist:
            continue

        # Get the last message for that contact
        last_msg = (
            Message.objects.filter(
                Q(sender=current_user, receiver=contact_user) |
                Q(sender=contact_user, receiver=current_user)
            ).order_by('-timestamp').first()
        )

        contacts.append({
            'user': contact_user.username,
            'profile_img': contact_user.profile_img.url if contact_user.profile_img else '/blank.webp',
            'last_message': last_msg.content if last_msg else '',
            'time': last_msg.timestamp.strftime('%H:%M') if last_msg else '',
        })
        seen.add(contact_id)

    # 👉 If this is an AJAX request, return JSON only
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'contacts': contacts})

    # Otherwise, render the normal HTML page
    return render(request, "frontpage.html", {
        'contacts': contacts,
        'username': current_user.username,
    })  
    
  
   
    
def chat_view(request, username, contact):
    """Show all messages between the logged-in user and selected contact."""
    current_user = get_object_or_404(CustomUser, username=username)
    contact_user = get_object_or_404(CustomUser, username=contact)

    # Normal page render
    messages = Message.objects.filter(
        Q(sender=current_user, receiver=contact_user) |
        Q(sender=contact_user, receiver=current_user)
    ).order_by("timestamp")

    return render(request, "details.html", {
        "contact": contact_user,
        "messages": messages,
        "username": current_user.username,
    })
    
    
def send_message(request):
    """Handle AJAX message send."""
    if request.method == "POST" and request.user.is_authenticated:
        sender = request.user
        receiver_username = request.POST.get("receiver")
        message_content = request.POST.get("message")

        if not receiver_username or not message_content.strip():
            return JsonResponse({"error": "Invalid message"}, status=400)

        try:
            receiver = get_object_or_404(CustomUser, username=receiver_username)
        except receiver.DoesNotExist:
            return JsonResponse({"error": "Receiver not found"}, status=404)
        
        try:
            sender = get_object_or_404(CustomUser, username=sender)
        except sender.DoesNotExist:
            return JsonResponse({"error": "Sender not found"}, status=404)

        msg = Message.objects.create(
            sender=sender,
            receiver=receiver,
            content=message_content.strip(),
            timestamp=timezone.now()
        )
        
        sender.add_friend(receiver)
        receiver.add_friend(sender)

        return JsonResponse({
            "sender": sender.username,
            "receiver": receiver.username,
            "content": msg.content,
            "timestamp": msg.timestamp.strftime("%H:%M"),
        })

    return JsonResponse({"error": "Unauthorized"}, status=403)


def fetch_messages(request, contact):
    """Fetch all messages (AJAX refresh)"""
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Unauthorized"}, status=403)

    contact_user = get_object_or_404(CustomUser, username=contact)

    messages = Message.objects.filter(
        Q(sender=request.user, receiver=contact_user) |
        Q(sender=contact_user, receiver=request.user)
    ).order_by("timestamp")

    data = [
        {
            "sender": msg.sender.username,
            "content": msg.content,
            "timestamp": msg.timestamp.strftime("%H:%M")
        } for msg in messages
    ]
    return JsonResponse({"messages": data})



def newFriend(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Unauthorized"}, status=403)

    current_user = request.user

    # Users who have already messaged or are friends
    messaged_user_ids = Message.objects.filter(
        Q(sender=current_user) | Q(receiver=current_user)
    ).values_list('sender', 'receiver')

    # Flatten list of tuples and remove current_user
    interacted_ids = set()
    for s, r in messaged_user_ids:
        if s != current_user.id:
            interacted_ids.add(s)
        if r != current_user.id:
            interacted_ids.add(r)

    interacted_ids.update(current_user.friends.values_list('id', flat=True))

    new_matches = CustomUser.objects.exclude(id__in=interacted_ids).exclude(id=current_user.id)

    context = {
        'username': current_user.username,
        'contacts': [],  # Keep chat list empty or load recent messages if needed
        'new_matches': new_matches,
    }
    return render(request, "newFriend.html", context)




def edit_message(request, msg_id):
    """Edit an existing message via AJAX."""
    if request.method == "POST" and request.user.is_authenticated:
        try:
            msg = Message.objects.get(id=msg_id, sender=request.user)
        except Message.DoesNotExist:
            return JsonResponse({"error": "Message not found"}, status=404)

        new_content = request.POST.get("content")
        if new_content and new_content.strip():
            msg.content = new_content.strip()
            msg.edited = True
            msg.save()
            return JsonResponse({
                "id": msg.id,
                "content": msg.content,
                "timestamp": msg.timestamp.strftime("%H:%M"),
                "edited": msg.edited
            })
    return JsonResponse({"error": "Unauthorized"}, status=403)



def delete_message(request, msg_id):
    """Delete a message via AJAX."""
    if request.method == "POST" and request.user.is_authenticated:
        try:
            msg = Message.objects.get(id=msg_id, sender=request.user)
        except Message.DoesNotExist:
            return JsonResponse({"error": "Message not found"}, status=404)

        msg.delete()
        return JsonResponse({"success": True, "id": msg_id})
    return JsonResponse({"error": "Unauthorized"}, status=403)



def profile(request):
    user = request.user
    errors = {}

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        bio = request.POST.get("bio", "").strip()
        phone_number = request.POST.get("phone_number", "").strip()
        profile_img = request.FILES.get("profile_img")

        # --- Validation ---
        if not username:
            errors['username'] = "Username cannot be empty."
        elif CustomUser.objects.filter(username=username).exclude(pk=user.pk).exists():
            errors['username'] = "This username is already taken."

        if not email:
            errors['email'] = "Email cannot be empty."
        elif CustomUser.objects.filter(email=email).exclude(pk=user.pk).exists():
            errors['email'] = "This email is already in use."
            
        if CustomUser.objects.filter(mobile_number=phone_number).exclude(pk=user.pk).exists():
            errors['email'] = "This phone number is already in use."

        # --- Update fields only if valid ---
        if not errors:
            updated = False 
            user = get_object_or_404(CustomUser, username=request.user)

            if username and username != user.username:
                user.username = username
                updated = True

            if email and email != user.email:
                user.email = email
                updated = True

            if bio and bio != user.bio:
                user.bio = bio
                updated = True
                
            if phone_number and phone_number != user.mobile_number:
                user.mobile_number = phone_number
                updated = True

            if profile_img:
                user.profile_img = profile_img
                updated = True

            # Save if any changes
            if updated:
                user.save()
                messages.success(request, "Profile updated successfully!")
            else:
                messages.info(request, "No changes detected.")

            return redirect('profile')  # reload page to show updates

    return render(request, "profile.html", {
        "user": user,
        "errors": errors
    })
    


@login_required
def view_profile(request, username):
    """View another user's profile (read-only)"""
    user_to_view = get_object_or_404(CustomUser, username=username)

    return render(request, "view_profile.html", {
        "user_to_view": user_to_view
    })



def search_users(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Unauthorized"}, status=403)

    query = request.GET.get('q', '').strip()

    if query == '':
        return JsonResponse({"results": []})

    # Search by username, email, or phone number
    users = CustomUser.objects.filter(
        Q(username__icontains=query) |
        Q(email__icontains=query) |
        Q(mobile_number__icontains=query)
    ).exclude(id=request.user.id)  # exclude current user

    results = []
    for user in users:
        results.append({
            'username': user.username,
            'email': user.email,
            'phone_number': user.mobile_number,
            'profile_img': user.profile_img.url if user.profile_img else '/blank.webp',
        })

    return JsonResponse({"results": results})