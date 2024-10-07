from django.forms import ModelForm
from .models import Rooms
from django.contrib.auth.models import User
class RoomsForm(ModelForm):
    class Meta:
        model = Rooms
        fields = '__all__'
        exclude= ['host','participants']

class UserForm (ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']