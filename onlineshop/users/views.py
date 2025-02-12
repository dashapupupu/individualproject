from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import UserProfile, DeliveryAddress, Order, User
from .forms import UserProfileForm, DeliveryAddressForm, EmailForm
from shop.models import Cart, Products, CartItem
import random
from django.core.mail import send_mail
from rest_framework.response import Response
from rest_framework.views import APIView

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
            cart_data = request.session.get('cart', [])
            if cart_data:
                cart, created = Cart.objects.get_or_create(user=user)
                for item in cart_data:
                    product = get_object_or_404(Products, pk=item['product_id'])
                    quantity = item['quantity']
                    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
                    cart_item.quantity += quantity
                    cart_item.save()
                del request.session['cart']
            return redirect('profile')
    else:
        form = UserCreationForm()
        profile_form = UserProfileForm()

    return render(request, 'register.html', {'form': form, 'profile_form': profile_form})

def user_login(request):
    if request.user.is_authenticated:
        return redirect('profile')
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            cart_data = request.session.get('cart', [])
            if cart_data:
                cart, created = Cart.objects.get_or_create(user=user)
                for item in cart_data:
                    product = get_object_or_404(Products, pk=item['product_id'])
                    quantity = item['quantity']
                    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
                    cart_item.quantity += quantity
                    cart_item.save()
                del request.session['cart']
            return redirect('profile')
        else:
            messages.error(request, "Неверное имя пользователя или пароль.")
    return render(request, 'login.html')

@login_required
def profile(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    delivery_addresses = DeliveryAddress.objects.filter(user=request.user)
    orders = Order.objects.filter(user=request.user).order_by('-order_date')
    return render(request, 'profile.html', {
        'user_profile': user_profile,
        'delivery_addresses': delivery_addresses,
        'orders': orders,
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

def logout_view(request):
    logout(request)
    return redirect('login')

def request_password_reset(request):
    if request.method == 'POST':
        form = EmailForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user_profile = UserProfile.objects.get(email=email)
                code = random.randint(100000, 999999)
                request.session['reset_code'] = code
                request.session['email'] = email
                send_mail(
                    'Код для восстановления пароля',
                    f'Ваш код для восстановления пароля: {code}',
                    'dididi2037@mail.ru',
                    [email],
                    fail_silently=False,
                )
                messages.success(request, 'Код для восстановления пароля отправлен на ваш email.')
                return redirect('verify_code')
            except UserProfile.DoesNotExist:
                messages.error(request, 'Пользователь с таким email не найден.')
    else:
        form = EmailForm()
    return render(request, 'request_password_reset.html', {'form': form})

def verify_code(request):
    if request.method == 'POST':
        entered_code = request.POST.get('code')
        if entered_code == str(request.session.get('reset_code')):
            return redirect('reset_password')
        else:
            messages.error(request, 'Неверный код. Попробуйте снова.')
    return render(request, 'verify_code.html')

def reset_password(request):
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        email = request.session.get('email')
        if email:
            try:
                user_profile = get_object_or_404(UserProfile, email=email)
                user = user_profile.user
                user.set_password(new_password)
                user.save()
                messages.success(request, 'Пароль успешно обновлен.')
                return redirect('login')
            except UserProfile.DoesNotExist:
                messages.error(request, 'Пользователь не найден.')
        else:
            messages.error(request, 'Сессия истекла. Пожалуйста, начните процесс сброса пароля заново.')
    return render(request, 'reset_password.html')




























from rest_framework.generics import get_object_or_404
from .serializers import UserProfileSerializer
from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.mixins import ListModelMixin
from .models import UserProfile


# User = get_user_model()

class UserProfileView(ListModelMixin, GenericAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
    def post(self, request, pk=None): # Registration
        if pk:
            return Response({"error":"Invalid request. POST requests should not have a pk"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = UserProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def put(self, request, pk): 
        profile = self.get_object(pk)
        if not profile:
            return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)
        if profile.user != request.user:
            return Response({'error':'Unauthorized to update this profile'}, status=status.HTTP_401_UNAUTHORIZED) #Additional security check

        serializer = UserProfileSerializer(profile, data=request.data, partial=True) #partial=True allows partial updates
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def delete(self, request, pk): 
        profile = self.get_object(pk)
        if not profile:
            return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)
        if profile.user != request.user:
            return Response({'error':'Unauthorized to delete this profile'}, status=status.HTTP_401_UNAUTHORIZED)

        profile.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
from rest_framework.permissions import AllowAny
class UserLoginView(APIView):
    authentication_classes = [] 
    permission_classes = [AllowAny]

    def post(self, request, format=None):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return Response({'message': 'Login successful'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    


class UserProfileDetailView(RetrieveUpdateDestroyAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    lookup_field = 'pk'




from rest_framework.decorators import api_view

@api_view(['GET', 'POST'])
def snippet_list(request, format=None):
    """
    List all user profiles or create a new user profile (registration).
    """
    if request.method == 'GET':
        profiles = UserProfile.objects.all()
        serializer = UserProfileSerializer(profiles, many=True)
        return Response(serializer.data)

    elif request.method == 'POST': # Registration
        serializer = UserProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET', 'PUT', 'DELETE'])
def snippet_detail(request, pk, format=None):
    """
    Retrieve, update, or delete a user profile.
    """
    try:
        profile = UserProfile.objects.get(pk=pk)
    except UserProfile.DoesNotExist:
        return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = UserProfileSerializer(profile, data=request.data, partial=True) #partial=True for partial updates
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        profile.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# from rest_framework.generics import get_object_or_404
# from rest_framework import status, viewsets
# from rest_framework.views import APIView
# from rest_framework.generics import GenericAPIView, RetrieveUpdateDestroyAPIView
# from rest_framework.mixins import ListModelMixin
# from .models import UserProfile
# from .serializers import UserProfileSerializer

# class UserProfileViewSet(viewsets.ViewSet):
#     """
#     A ViewSet for managing UserProfiles.
#     """
#     def list(self, request):
#         queryset = UserProfile.objects.all()
#         serializer = UserProfileSerializer(queryset, many=True)
#         return Response(serializer.data)

#     def retrieve(self, request, pk=None):
#         queryset = UserProfile.objects.all()
#         user_profile = get_object_or_404(queryset, pk=pk)
#         serializer = UserProfileSerializer(user_profile)
#         return Response(serializer.data)

#     def create(self, request):
#         serializer = UserProfileSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def update(self, request, pk=None):
#         user_profile = get_object_or_404(UserProfile.objects.all(), pk=pk)
#         serializer = UserProfileSerializer(user_profile, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def destroy(self, request, pk=None):
#         user_profile = get_object_or_404(UserProfile.objects.all(), pk=pk)
#         user_profile.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)