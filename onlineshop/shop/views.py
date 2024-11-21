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
    categories_list = Categories.objects.all()# получка всех категорий
    all_products = Products.objects.all() # получка всех продуктов
     

    #проверкрка
    category_id = request.GET.get('category')

    #вывод
    if category_id:
        products = Products.objects.filter(categories_id=category_id)
    else:
        products = all_products # если не выбрано

    context = {
        'products': products,
        'categories_list': categories_list,
    }

    return render(request, 'index.html', context)

