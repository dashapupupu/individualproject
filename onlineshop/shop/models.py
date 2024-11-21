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
 price = models.CharField(max_length=100, help_text="Введите цену продукта: ", verbose_name="Цена")
 categories = models.ForeignKey('categories', on_delete=models.CASCADE, help_text="Выберите категорию продукта: ", verbose_name="Категория", null=True)
 image = models.ImageField(upload_to='products/')
 proizvoditel = models.ForeignKey('proizvoditel', on_delete=models.CASCADE, help_text="Выберите производителя: ", verbose_name="Производитель", null=True)
 kcal = models.PositiveIntegerField(help_text="Введите калорийность продукта: ", verbose_name="Калорийность", null=True, blank=True)
 def __str__(self):
    return self.name
 


