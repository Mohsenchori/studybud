from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class Topic(models.Model):
    topic_name = models.CharField(max_length=200)

    def __str__(self):
        return self.topic_name

# costumized user model
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture= models.ImageField(upload_to='profile_pictures/',blank=True, null=True, default='profile_pictures/default-avatar.svg')
    def __str__(self):
        return f'{self.user.username} Profile'
    

class Rooms(models.Model):
    host= models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    topic= models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length= 200)
    description = models.TextField(null=True, blank=True)
    participants = models.ManyToManyField(User, related_name='participants', blank=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-updated','-created']
    def __str__(self):
        return self.name

class Message(models.Model):
    user = models.ForeignKey(User, on_delete= models.CASCADE)
    room = models.ForeignKey(Rooms, on_delete= models.CASCADE)
    body = models.TextField()
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.body[0:50]
    

class visit(models.Model):
    path = models.CharField(max_length=250)
    
class Follow (models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name= 'following')
    followed = models.ForeignKey(User, on_delete=models.CASCADE, related_name= 'follower')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('follower', 'followed') # prevent duplicate following
        
class Notification (models.Model):
    recipient = models.ForeignKey(User , on_delete=models.CASCADE , related_name='notifications')
    actor = models.ForeignKey (User, on_delete=models.CASCADE, related_name='activities')
    message = models.TextField()
    room = models.ForeignKey (Rooms, on_delete=models.CASCADE , null=True, blank= True)
    is_read = models.BooleanField (default=False)
    created_at = models.DateTimeField (auto_now_add= True)