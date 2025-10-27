from django.contrib import admin

# Register your models here.

from .models import (
    Dish,
    Product,
    TechnologicalMap,
    TechnologicalMapComposition,
    FoodCategory,
)

admin.site.register(Dish)
admin.site.register(FoodCategory)

admin.site.register(Product)

admin.site.register(TechnologicalMap)
admin.site.register(TechnologicalMapComposition)
