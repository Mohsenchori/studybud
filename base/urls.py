
from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name = 'homeurl'),
    path('create-room', views.createRoom, name = 'createRoomurl'),
    path('update-room/<str:pk>', views.updateRoom, name = 'updateRoomurl'),
    path('delete-room/<str:pk>', views.deleteRoom, name = 'deleteRoomurl'),
    path('delete-comment/<str:pk>', views.deleteComment, name = 'deleteCommenturl'),
    path('rooms/<str:pk>/', views.room, name = 'roomurl'),
    path('login/', views.loginPage, name = 'loginurl'),
    path('profile/<str:pk>/', views.userProfile, name = 'profileurl'),
    path('register/', views.registerUser, name = 'registerurl'),
    path('logout/', views.logoutUser, name = 'logouturl'),
    path('update-user/', views.updateUser, name = 'updateuserurl'),
    path('topics/', views.topics_page, name = 'topicpageurl'),
    
]
