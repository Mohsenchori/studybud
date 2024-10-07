from django.contrib import admin

# Register your models here.
from .models import Rooms,Topic,Message

class RoomsAdmin(admin.ModelAdmin):
    list_display = ('name', 'topic','host')
admin.site.register(Rooms, RoomsAdmin)
admin.site.register(Topic)
admin.site.register(Message)