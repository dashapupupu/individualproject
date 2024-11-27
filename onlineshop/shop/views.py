from django.shortcuts import render
from .models import Products
from .models import Categories


def index(request):
 return render(request, "index.html")

def about(request):
 return render(request, "shop/about.html")


def contact(request):
 return render(request, "shop/contact.html")



def index(request):
    categories_list = Categories.objects.all()  # все категории 
    all_products = Products.objects.all()  # все запросы

    # получени параметра из запроса
    category_id = request.GET.get('category')
    search_query = request.GET.get('search', '')
    sort_option = request.GET.get('sort', '')

    # фильтр по категории
    if category_id:
        products = all_products.filter(categories_id=category_id)
    else:
        products = all_products  # Если не выбрано

    # нечувств регистр
    if search_query:
        products = products.filter(name__icontains=search_query)
        

    # фильтр по цене
    if sort_option == 'asc':
        products = products.order_by('price')  # по возрастанию
    elif sort_option == 'desc':
        products = products.order_by('-price')  # по убыванию

    context = {
        'products': products,
        'categories_list': categories_list,
    }

    return render(request, 'index.html', context)






from django.shortcuts import render, redirect, get_object_or_404
from .models import Products
from django.http import JsonResponse
def add_to_cart(request, product_id):
    #  как список
    cart = request.session.get('cart', [])
    
  
    if not isinstance(cart, list):
        print("Ошибка: cart не является списком, инициализируем как пустой список.")
        cart = []

    print("Текущая корзина:", cart)  

  
    product_exists = next((item for item in cart if isinstance(item, dict) and item.get('product_id') == product_id), None)

    if product_exists:
        product_exists['quantity'] += 1
    else:
        cart.append({'product_id': product_id, 'quantity': 1})

    request.session['cart'] = cart  
    return JsonResponse({'success': True, 'message': 'Товар успешно добавлен в корзину!'})


def remove_from_cart(request, product_id):
   
    cart = request.session.get('cart', [])
    
    
    if not isinstance(cart, list):
        print("Ошибка: cart не является списком, инициализируем как пустой список.")
        cart = []

    print("Текущая корзина:", cart)  

   
    item_to_remove = next((item for item in cart if isinstance(item, dict) and item.get('product_id') == product_id), None)

    if item_to_remove:
        cart.remove(item_to_remove)
    else:
        print(f"Товар {product_id} не найден в корзине.")

    request.session['cart'] = cart  
    return redirect('cart')


def update_cart(request, product_id):
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        cart = request.session.get('cart', [])
        
      
        if not isinstance(cart, list):
            print("Ошибка: cart не является списком, инициализируем как пустой список.")
            cart = []

        if quantity > 0:
          
            item_to_update = next((item for item in cart if item.get('product_id') == product_id), None)
            if item_to_update:
                item_to_update['quantity'] = quantity
            else:
                cart.append({'product_id': product_id, 'quantity': quantity})
        else:
        
            cart = [item for item in cart if item.get('product_id') != product_id]

        request.session['cart'] = cart
    return redirect('cart')


def cart(request):
    cart = request.session.get('cart', [])
    cart_items = []
    total = 0
    
 
    if not isinstance(cart, list):
        print("Ошибка: cart не является списком, инициализируем как пустой список.")
        cart = []

    for item in cart:
        product_id = item.get('product_id')
        quantity = item.get('quantity', 0)
        product = get_object_or_404(Products, pk=product_id)
        price_with_discount = product.price * (1 - product.discount / 100)  
        item_total = price_with_discount * quantity
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'item_total': item_total,
            'price_with_discount': price_with_discount  
        })
        total += item_total
    
    context = {'cart_items': cart_items, 'total': total}
    return render(request, 'cart/cart.html', context)
