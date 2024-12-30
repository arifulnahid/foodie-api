from django.db import models
from django.contrib.auth.models import User
from food.models import FoodItem

# Create your models here.

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    class Meta:
        unique_together = ['user', 'food_item']

    def __str__(self):
        return self.user.username
    
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    food_items = models.ManyToManyField(FoodItem)
    total = models.IntegerField(null=False)
    discount = models.IntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length= 20, choices= [
        ('Pending', 'Pending'), 
        ('Failed', 'Failed'), 
        ('Delivered', 'Delivered')
        ], default='Pending')
    payment = models.CharField(max_length=20, choices=[
        ('Cash', 'Cash'), 
        ('Bank', 'Bank'), 
        ('Mobile Banking', 'Mobile Banking')
        ], default='Cash')
    
    def __str__(self):
        return f'{self.user.username} | {self.date}'
