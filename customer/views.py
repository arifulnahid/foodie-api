from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import authenticate, login, logout
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.shortcuts import redirect
from django_filters.rest_framework import DjangoFilterBackend
from . import models
from food.models import FoodItem
from . import serializers

# Create your views here.
class CustomerRegister(APIView):
    serializer_class = serializers.RegisterSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            customer = serializers.CustomerSerializer(user, many=False)
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))

            email_subject = "Confirm Your Email"
            email_body = render_to_string('confirm_email.html', {"token":token, "uid": uid})
            email = EmailMultiAlternatives(email_subject, '', to=[user.email])
            email.attach_alternative(email_body, 'text/html')
            email.send()
            return Response("Check your mail for confirmation")
        return Response({'error': serializer.errors})
    
def activate(request, uid64, token):
    try:
        uid = urlsafe_base64_decode(uid64).decode()
        user = User._default_manager.get(pk=uid)
    except(User.DoesNotExist):
        user = None 
    
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return redirect('login')
    else:
        return Response({'message': 'Your account activation faild'})

class CustomerLogin(APIView):
    serializer_class = serializers.LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=self.request.data)

        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            
            user = authenticate(username=username, password=password)

            if user:
                customer = serializers.CustomerSerializer(user, many=False)
                token, _ = Token.objects.get_or_create(user=user)
                login(request, user)
                return Response({'token': token.key, 'customer': customer.data})
            else:
                return Response({'error': 'Invalid Credential'})
        return Response(serializer.errors)


class CustomerLogout(APIView):
    def get(self, request):
        request.user.auth_token.delete()
        logout(request)
        return redirect('login')

class CartViewSet(viewsets.ModelViewSet):
    queryset = models.Cart.objects.all()
    serializer_class = serializers.CartSerializer
    # permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        food_item = request.data.get('food_item')
        if not food_item and not request.user.is_authenticated:
            return Response({"error": "Provide all values and Authentication"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            food = FoodItem.objects.get(pk=food_item)
        except FoodItem.DoesNotExist:
            return Response({"error": "Invalid Food ID"}, status=status.HTTP_400_BAD_REQUEST) 

        cart_item, created = models.Cart.objects.get_or_create(user=request.user, food_item=food)
        if not created :
            cart_item.quantity+=1
            cart_item.save()    
            serializer = self.get_serializer(cart_item)
            return Response(serializer.data, status=status.HTTP_200_OK)  
            
        serializer = self.get_serializer(cart_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    
    def list(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response({'error': 'Access forbidden'}, status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)
        
        queryset = self.filter_queryset(self.get_queryset().filter(user=request.user))
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def partial_update(self, request, pk=None):
        type = request.data.get('type')
        
        try:
            cart_item = models.Cart.objects.get(pk=pk, user=request.user)
        except models.Cart.DoesNotExist:
            return Response({'error': 'Cart Does not exist'})
                
        if cart_item:
            if type == 'increase':
                cart_item.quantity+=1
            else:
                if cart_item.quantity > 1:
                    cart_item.quantity-=1
            
            cart_item.save()
            serializer = self.get_serializer(cart_item)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, pk=None):
        try:
            cart_item = models.Cart.objects.get(pk=pk, user=request.user)
        except models.Cart.DoesNotExist:
            return Response({'error': 'Cart item does not exit'})
        
        cart_item.delete()
        return Response({'message': 'Delete Successful'}, status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=False, methods=['delete'], url_path='bulk-delete') 
    def bulk_delete(self, request): 
        ids = request.data.get('ids', []) 
        if not ids: 
            return Response({'error': 'No IDs provided'}, status=status.HTTP_400_BAD_REQUEST) 
        models.Cart.objects.filter(id__in=ids).delete() 
        return Response({'message': 'Entries deleted'}, status=status.HTTP_204_NO_CONTENT)

class OrderViewSet(viewsets.ModelViewSet):
    queryset = models.Order.objects.all()
    serializer_class = serializers.OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user']
