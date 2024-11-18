from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .models import Rooms, Topic, Message, visit
from .forms import RoomsForm, UserForm

# we use function based views 

# we have a single html page for both login and registering
def loginPage(request):
    # to tell the template which view has rendered it 
    page = 'login'
    
    # redirect to home page if its logged in already
    if request.user.is_authenticated:
        return redirect('homeurl')
    
    # match the username and password from the form to the database
    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')
        # we can delete this block but we wont know which field is incorrect
        try:
            User.objects.get(username=username)
        except:
            messages.error(request, 'username not found')
        # lets check now
        user = authenticate(request, username=username, password=password)
        # if the method returns true then we use login method to login and go back to home page
        if user is not None:
            login(request, user)
            return redirect('homeurl')
        else:
            messages.error(request, 'wrong password')
    
    # rendering ...
    context = {'page': page}
    return render(request, 'base/login_register.html',context)


# we are using django's login and logout library and the default user model
def logoutUser(request):
    logout(request)
    return redirect('homeurl')

def registerUser(request):
    # to tell the template its the registerUser view
    page = registerUser
    # using django pre-build forms
    form = UserCreationForm()
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # to make sure all usenames are saved in lower case
            user.username = user.username.lower()
            user.save()
            # after creating a new user we call the login view to log the user in
            login(request,user)
            return redirect('homeurl')
    else:
        messages.error(request, ' an error occurred during registration')
    # rendering ...
    context= {'page': page , 'form' : form}
    return render(request,'base/login_register.html', context)

# home page view
def home(request):
    # storing query params, we use 'q' character to name it
    q = request.GET.get('q') if request.GET.get('q') else ''
    # *** django orm query - filter returns list
    rooms = Rooms.objects.filter(
        Q(topic__topic_name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
    )
    # we also want 5 of our topic names and roomcount to generate the template
    topics = Topic.objects.all()[0:5]
    room_count = rooms.count()
    
    # to show the latest messages , but we use filter so we can find certain mesaages for rooms searched for
    # -created means latests first
    latests = Message.objects.filter(Q(
        room__topic__topic_name__icontains=q
    )).order_by('-created')
    
    # rendering...
    context = {'room': rooms, 'topics': topics, 'room_count': room_count, 'latest': latests, 'all_rooms' : Rooms.objects.count()}
    return render(request, 'base/home.html', context)

# room view needs a pk(primary key) to find the chosen room
def room(request, pk):
    room = Rooms.objects.get(id=pk)
    # getting a list of mesaages related to the room 
    comments = room.message_set.all().order_by('-created')
    # a counter to count visits of the room
    visit.objects.create(path = request.path)
    visits = visit.objects.filter(path = request.path)
    
    participants = room.participants.all()
    # hanling new comment
    if request.method == 'POST':
        comment = Message.objects.create(
            user = request.user,
            room = room,
            body = request.POST.get('body')
        )
        room.participants.add(request.user)
        #we can do it without redirect but its safer due to posting
        return redirect('roomurl', pk = room.id)
    context = {'room': room ,'comments': comments, 'participants': participants, 'visits' : visits.count}
    return render(request, 'base/room.html', context)

# user profile view
def userProfile(request,pk):
    user = User.objects.get(id=pk)
    rooms = user.rooms_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context={'user': user, 'room':rooms, 'latest': room_messages, 'topics': topics}
    return render(request,'base/profile.html',context)

# view for creating room, this view reqieres the user to login to be able to access to it
@login_required(login_url='loginurl')
def createRoom(request):
    form = RoomsForm()
    topics = Topic.objects.all()
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        
        # topic, created = Topic.objects.get_or_create(topic_name = topic_name)
        topic= Topic.objects.get_or_create(topic_name = topic_name)
        Rooms.objects.create(
            host = request.user,
            topic = topic,
            name = request.POST.get('name'),
            description = request.POST.get('description')
        )
        # form = RoomsForm(request.POST)
        # if form.is_valid():
        #     room = form.save(commit=False)
        #     room.host=  request.user
        #     room.save()
        return redirect('homeurl')
    context = {'form': form, 'requestuser': request.user, 'topics': topics}
    return render(request, 'base/room_form.html', context)

# UPDATING room view. it requires the user to be logged in , if user is not logged in the decorator redirects him to the login url
@login_required(login_url='loginurl')
def updateRoom(request, pk):
    topics = Topic.objects.all()
    room = Rooms.objects.get(id=pk)
    form = RoomsForm(instance=room)
    if request.user != room.host:
        return HttpResponse('youre not the one')
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(topic_name = topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
    
        
        # form = RoomsForm(request.POST, instance=room)
        # if form.is_valid():
        #     form.save()
        return redirect('homeurl')

    context = {'form': form , 'topics': topics, 'room': room}
    return render(request, 'base/room_form.html', context)


# deleting room
@login_required(login_url='loginurl')
def deleteRoom(request, pk):
    room = Rooms.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse('youre not the one')

    if request.method == 'POST':
        room.delete()
        return redirect('homeurl')
    return render(request, 'base/delete.html', {'obj': room})

# deleting message
@login_required(login_url='loginurl')
def deleteComment(request, pk):
    comment = Message.objects.get(id=pk)

    if request.user != comment.user:
        return HttpResponse('youre not the one')

    if request.method == 'POST':
        comment.delete()
        return redirect('homeurl')
    return render(request, 'base/delete.html', {'obj': comment})


@login_required(login_url='loginurl')
def updateUser(request):
    user= request.user
    form = UserForm(instance=user)
    if request.method == 'POST':
        form = UserForm(request.POST , instance=user)
        if form.is_valid():
            form.save()
            return redirect('profileurl' , pk = user.id)
    context = {
        'user': user,
        'form' : form
    }
    return render(request, 'base/update-user.html',context)

# for achieving the full list of the topics
def topics_page (request):
    
    q = request.GET.get('q') if request.GET.get('q') else ''
    topics = Topic.objects.filter(topic_name__icontains=q)
    context = {'topics': topics}
    return render (request, 'base/topics.html', context)