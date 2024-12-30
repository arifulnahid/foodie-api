from django.contrib import admin
from . import models

# Register your models here.
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'food_item', 'quantity']

class OrderInline(admin.TabularInline):
    model = models.Order.food_items.through
    extra = 1

class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderInline]
    exclude = ('food_items',)
    list_display = ['user', 'total', 'date']

admin.site.register(models.Cart, CartAdmin)
admin.site.register(models.Order, OrderAdmin)
