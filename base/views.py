from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .models import Rooms, Topic, Message
from .forms import RoomsForm, UserForm

# Create your views here.
# rooms = [
#     {'id': 1, 'name': 'lets learn python'},
#     {'id': 2, 'name': 'lets learn js'},
#     {'id': 3, 'name': 'lets learn c++'},
#     {'id': 4, 'name': 'lets learn c#'},
# ]


# we have a single html page for both login and registering
# we find out which we want to work with with a page variable
def loginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('homeurl')
    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')
        try:
            User.objects.get(username=username)
        except:
            messages.error(request, 'username not found')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('homeurl')
        else:
            messages.error(request, 'wrong password')
    context = {'page': page}
    return render(request, 'base/login_register.html',context)

# we are using django's login and logout library and user model , i should study about costum ones
def logoutUser(request):
    logout(request)
    return redirect('homeurl')

def registerUser(request):

    page = registerUser
    form = UserCreationForm()
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request,user)
            return redirect('homeurl')
    else:
        messages.error(request, ' an error occurred during registration')
    context= {'page': page , 'form' : form}
    return render(request,'base/login_register.html', context)


def home(request):
    q = request.GET.get('q') if request.GET.get('q') else ''
    rooms = Rooms.objects.filter(
        Q(topic__topic_name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
    )
    topics = Topic.objects.all()[0:5]
    room_count = rooms.count()
    latests = Message.objects.filter(Q(
        room__topic__topic_name__icontains=q
    )).order_by('-created')
    #user = User.objects.get(username = request.user.username)
    context = {'room': rooms, 'topics': topics, 'room_count': room_count, 'latest': latests, 'all_rooms' : Rooms.objects.count()}
    return render(request, 'base/home.html', context)


def room(request, pk):
    room = Rooms.objects.get(id=pk)
    comments = room.message_set.all().order_by('-created')
    #comments = Message.objects.get(room = pk)
    participants = room.participants.all()
    if request.method == 'POST':
        comment = Message.objects.create(
            user = request.user,
            room = room,
            body = request.POST.get('body')
        )
        room.participants.add(request.user)
        #we can do it without redirect but its safer due to posting
        return redirect('roomurl', pk = room.id)
    context = {'room': room ,'comments': comments, 'participants': participants}
    return render(request, 'base/room.html', context)

def userProfile(request,pk):
    user = User.objects.get(id=pk)
    rooms = user.rooms_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context={'user': user, 'room':rooms, 'latest': room_messages, 'topics': topics}
    return render(request,'base/profile.html',context)


@login_required(login_url='loginurl')
def createRoom(request):
    form = RoomsForm()
    topics = Topic.objects.all()
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(topic_name = topic_name)
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

@login_required(login_url='loginurl')
def deleteRoom(request, pk):
    room = Rooms.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse('youre not the one')

    if request.method == 'POST':
        room.delete()
        return redirect('homeurl')
    return render(request, 'base/delete.html', {'obj': room})

def deleteComment(request, pk):
    comment = Message.objects.get(id=pk)

    if request.user != comment.user:
        return HttpResponse('youre not the one')

    if request.method == 'POST':
        comment.delete()
        return redirect('homeurl')
    return render(request, 'base/delete.html', {'obj': comment})

@login_required
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

def topics_page (request):
    
    q = request.GET.get('q') if request.GET.get('q') else ''
    topics = Topic.objects.filter(topic_name__icontains=q)

    context = {'topics': topics}
    
    return render (request, 'base/topics.html', context)