from django_filters import rest_framework as filters
from . import models

class FoodItemFilter(filters.FilterSet):
    category_name = filters.CharFilter(field_name='category__name', lookup_expr='icontains')    
    discount__gt = filters.NumberFilter(field_name='discount', lookup_expr='gt')
    class Meta:
        model = models.FoodItem
        fields = ['category_name', 'discount__gt']

