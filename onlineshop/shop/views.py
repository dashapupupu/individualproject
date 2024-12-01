from django.shortcuts import render, redirect, get_object_or_404
from .models import Products, Cart, CartItem, Categories
from django.http import JsonResponse
from users.models import UserProfile, Order, OrderItem, DeliveryAddress
from django.core.mail import send_mail
from django.contrib import messages

def index(request):
    categories_list = Categories.objects.all()
    all_products = Products.objects.all()
    category_id = request.GET.get('category')
    search_query = request.GET.get('search', '')
    sort_option = request.GET.get('sort', '')

    if category_id:
        products = all_products.filter(categories_id=category_id)
    else:
        products = all_products

    if search_query:
        products = products.filter(name__icontains=search_query)

    if sort_option == 'asc':
        products = products.order_by('price')
    elif sort_option == 'desc':
        products = products.order_by('-price')

    context = {
        'products': products,
        'categories_list': categories_list,
    }

    return render(request, 'index.html', context)

def about(request):
    return render(request, "shop/about.html")

def contact(request):
    return render(request, "shop/contact.html")

def add_to_cart(request, product_id):
    product = get_object_or_404(Products, id=product_id)

    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

        if created:
            cart_item.quantity = 1
        else:
            cart_item.quantity += 1

        cart_item.save()
    else:
        cart = request.session.get('cart', [])
        for item in cart:
            if item['product_id'] == product_id:
                item['quantity'] += 1
                break
        else:
            cart.append({'product_id': product_id, 'quantity': 1})
        request.session['cart'] = cart

    return JsonResponse({'success': True, 'message': 'Товар успешно добавлен в корзину!'})

def remove_from_cart(request, product_id):
    if request.user.is_authenticated:
        cart = get_object_or_404(Cart, user=request.user)
        cart_item = get_object_or_404(CartItem, cart=cart, product_id=product_id)
        cart_item.delete()
    else:
        cart = request.session.get('cart', [])
        cart = [item for item in cart if item['product_id'] != product_id]
        request.session['cart'] = cart

    return redirect('cart')

def update_cart(request, product_id):
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))

        if request.user.is_authenticated:
            cart = get_object_or_404(Cart, user=request.user)

            if quantity > 0:
                cart_item, created = CartItem.objects.get_or_create(cart=cart, product_id=product_id)
                cart_item.quantity = quantity
                cart_item.save()
            else:
                cart_item = get_object_or_404(CartItem, cart=cart, product_id=product_id)
                cart_item.delete()
        else:
            cart = request.session.get('cart', [])
            for item in cart:
                if item['product_id'] == product_id:
                    if quantity > 0:
                        item['quantity'] = quantity
                    else:
                        cart.remove(item)
                    break
            request.session['cart'] = cart

    return redirect('cart')

def cart(request):
    cart_items = []
    total = 0
    delivery_addresses = []

    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_items = CartItem.objects.filter(cart=cart)
        total = sum(item.product.price * item.quantity * (1 - item.product.discount / 100) for item in cart_items)
        delivery_addresses = DeliveryAddress.objects.filter(user=request.user)

        cart_items = [{
            'product': item.product,
            'quantity': item.quantity,
            'item_total': item.product.price * item.quantity * (1 - item.product.discount / 100),
            'price_with_discount': item.product.price * (1 - item.product.discount / 100)
        } for item in cart_items]

    else:
        cart_data = request.session.get('cart', [])
        for item in cart_data:
            product = get_object_or_404(Products, pk=item['product_id'])
            quantity = item['quantity']
            price_with_discount = product.price * (1 - product.discount / 100)
            item_total = price_with_discount * quantity
            
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'item_total': item_total,
                'price_with_discount': price_with_discount
            })

        total = sum(item['item_total'] for item in cart_items)

    if request.method == 'POST':
        delivery_address_id = request.POST.get('delivery_address')

        if delivery_address_id:
            order = Order.objects.create(
                user=request.user,
                delivery_address=DeliveryAddress.objects.get(id=delivery_address_id),
                total=total
            )

            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    quantity=item['quantity'],
                    price=item['price_with_discount']
                )

            CartItem.objects.filter(cart=cart).delete()

            order_details = f'Заказ №{order.id}\n'
            order_details += f'Пользователь: {order.user.username}\n'
            order_details += f'Адрес доставки: {order.delivery_address}\n'
            order_details += f'Сумма заказа: {order.total}\n'
            order_details += 'Детали заказа:\n'
            for item in order.items.all():
                order_details += f'- {item.product.name}: {item.quantity} шт. по {item.price} руб.\n'

            user_profile = UserProfile.objects.get(user=order.user)
            user_email = user_profile.email
            fixed_recipient = 'dididi2037@mail.ru'

            send_mail(
                'Подтверждение вашего заказа',
                order_details,
                'kopochko345@mail.ru',
                [user_email, fixed_recipient],
                fail_silently=False,
            )

            messages.success(request, 'Ваш заказ успешно оформлен! Подробности были отправлены на вашу почту.')
            return render(request, 'cart/order_success.html', {'order': order})

    return render(request, 'cart/cart.html', {
        'cart_items': cart_items,
        'total': total,
        'delivery_addresses': delivery_addresses,
    })
