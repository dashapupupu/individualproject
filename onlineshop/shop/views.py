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