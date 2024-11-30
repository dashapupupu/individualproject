from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import UserProfile, DeliveryAddress
from .forms import UserProfileForm, DeliveryAddressForm



def register(request):
    if request.user.is_authenticated:
        return redirect('profile')

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        profile_form = UserProfileForm(request.POST, request.FILES)
        if form.is_valid() and profile_form.is_valid():
            user = form.save()
            profile = profile_form.save(commit=False)
            profile.user = user  
            profile.save() 
            login(request, user)  
            return redirect('profile')  
    else:
        form = UserCreationForm()
        profile_form = UserProfileForm()

    return render(request, 'register.html', {'form': form, 'profile_form': profile_form})


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('profile')  
        else:
            messages.error(request, "Неверное имя пользователя или пароль.") 
    return render(request, 'login.html')


@login_required
def profile(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    delivery_addresses = DeliveryAddress.objects.filter(user=request.user)
    return render(request, 'profile.html', {
        'user_profile': user_profile,
        'delivery_addresses': delivery_addresses, 
    })


@login_required
def edit_profile(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Профиль обновлен.")
            return redirect('profile')
    else:
        form = UserProfileForm(instance=user_profile)
    return render(request, 'account.html', {'form': form}) 


@login_required
def add_delivery_address(request):
    if request.method == 'POST':
        form = DeliveryAddressForm(request.POST)
        if form.is_valid():
            delivery_address = form.save(commit=False)
            delivery_address.user = request.user
            delivery_address.save()
            messages.success(request, "Адрес доставки добавлен.")
            return redirect('profile')
    else:
        form = DeliveryAddressForm()
    return render(request, 'add_address.html', {'form': form}) 


@login_required
def delete_delivery_address(request, address_id):
    address = get_object_or_404(DeliveryAddress, id=address_id, user=request.user)
    address.delete()
    messages.success(request, "Адрес доставки удален.")
    return redirect('profile')
from django.contrib.auth import logout
def logout_view(request):
    logout(request)  
    return redirect('login')  