from django.contrib import admin
from . import models

# Register your models here.
class FoodAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'quantity']

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields ={'slug': ('name',)}

class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'food_item', 'rating', 'comment', 'created_at']

admin.site.register(models.FoodItem, FoodAdmin);
admin.site.register(models.Category, CategoryAdmin);
admin.site.register(models.Review, ReviewAdmin);