from django.db import models
from django.urls import reverse


class Categories(models.Model):
 name = models.CharField(max_length=20,
 help_text="Введите категорию продукта", verbose_name="Категория продукта")
 def __str__(self):
    return self.name
 
class Proizvoditel(models.Model):
 name = models.CharField(max_length=20,
 help_text="Введите производителя: ", verbose_name="Производитель")
 def __str__(self):
    return self.name
 
class Products(models.Model):
    name = models.CharField(max_length=100, help_text="Введите название продукта: ", verbose_name="Название продукта")
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Введите цену продукта: ", verbose_name="Цена")
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text="Введите скидку на продукт: ", verbose_name="Скидка")
    description = models.TextField(help_text="Введите описание продукта: ", verbose_name="Описание", default='Описание отсутствует.')
    categories = models.ForeignKey('Categories', on_delete=models.CASCADE, help_text="Выберите категорию продукта: ", verbose_name="Категория", null=True)
    image = models.ImageField(upload_to='products/')
    proizvoditel = models.ForeignKey('Proizvoditel', on_delete=models.CASCADE, help_text="Выберите производителя: ", verbose_name="Производитель", null=True)

    def __str__(self):
        return self.name
 


