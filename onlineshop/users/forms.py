from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from .models import UserProfile, DeliveryAddress
from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import UserProfile, DeliveryAddress




from django import forms
from .models import UserProfile

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['email', 'phone_number', 'address', 'city', 'birth_date', 'avatar']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'avatar': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }
        labels = {
            'email': 'Адрес электронной почты',
            'phone_number': 'Номер телефона',
            'address': 'Адрес',
            'city': 'Город',
            'birth_date': 'Дата рождения (Необязательно)',
            'avatar': 'Аватар (Необязательно)',
        }

class DeliveryAddressForm(forms.ModelForm):
    class Meta:
        model = DeliveryAddress
        fields = ['address', 'city']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 2}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'address': 'Адрес доставки',
            'city': 'Город',
        }





from django import forms

class EmailForm(forms.Form):
    email = forms.EmailField(label='Email')