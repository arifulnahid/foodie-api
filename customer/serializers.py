from rest_framework import serializers
from django.contrib.auth.models import User
from . import models
from food.serializers import FoodSerializer

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']

class RegisterSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password', 'confirm_password')

    def save(self):
        username = self.validated_data['username']
        email = self.validated_data['email']
        first_name = self.validated_data['first_name']
        last_name = self.validated_data['last_name']
        password = self.validated_data['password']
        confirm_password = self.validated_data['confirm_password']

        if password != confirm_password:
            raise serializers.ValidationError({'error': 'Password Does\'t Match'})
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({'error': 'Email Already Exist'})
        
        account = User(username=username, email=email, first_name=first_name, last_name=last_name)
        account.set_password(password)
        account.is_active = False
        account.save()
        return account

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

class CartSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    food_item = FoodSerializer(many=False, read_only=True)

    class Meta:
        model = models.Cart
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    # food_items = serializers.StringRelatedField(many=True)
    food_items_display = serializers.StringRelatedField(many=True, source="food_items", read_only=True)
    class Meta:
        model = models.Order
        fields = '__all__'
        read_only_fields = ['food_items_display']