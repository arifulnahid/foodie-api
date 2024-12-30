from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=120)
    slug= models.SlugField(max_length=255, unique=True)

    def __str__(self):
        return self.name 


class FoodItem(models.Model):
    name = models.CharField(max_length=30)
    price = models.IntegerField(default=0)
    description = models.TextField()
    quantity = models.IntegerField(default=0)
    image = models.ImageField(upload_to='images/food')
    discount = models.IntegerField(default=0)
    delivery_time = models.CharField(max_length=120, null=True)
    category = models.ForeignKey(Category, null=True, on_delete=models.CASCADE);

    def __str__(self):
        return self.name 
    

RATING = [
    ('⭐', '⭐'),
    ('⭐⭐', '⭐⭐'),
    ('⭐⭐⭐', '⭐⭐⭐'),
    ('⭐⭐⭐⭐', '⭐⭐⭐⭐'),
    ('⭐⭐⭐⭐⭐', '⭐⭐⭐⭐⭐'),
]
class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    comment = models.TextField()
    rating = models.CharField(max_length=5, default='1')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.food_item.name
    
    class Meta:
        unique_together = ['user', 'food_item']