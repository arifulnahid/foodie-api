from rest_framework import viewsets, filters, permissions, views, response, status
from rest_framework.pagination import LimitOffsetPagination
from django_filters.rest_framework import DjangoFilterBackend
from . import serializers
from . import models
from . import filter

# Create your views here.
class FoodItemViewset(viewsets.ModelViewSet):
    queryset = models.FoodItem.objects.all()
    serializer_class = serializers.FoodSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = filter.FoodItemFilter
    pagination_class = LimitOffsetPagination
    search_fields = ['name','description', 'category__name']
    ordering_fields = ['discount']

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = models.Category.objects.all()
    serializer_class = serializers.CategorySerializer

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = models.Review.objects.all()
    serializer_class = serializers.ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['food_item', 'user']

    def create(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return response.Response({'error': 'Authentication required'}, status=status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED)
        
        serializer = serializers.ReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return response.Response(serializer.data)
        return response.Response(serializer.error)

class ReviewAPIView(views.APIView):
    serializer_class = serializers.ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, food_key):
        try: 
            food = models.FoodItem(pk=food_key)
        except food.DoesNotExist:
            return response.Response({'error': 'Food not found'}, status=status.HTTP_404_NOT_FOUND)
        
        reviews = models.Review.objects.filter(food_item=food)
        serializer = serializers.ReviewSerializer(reviews, many=True)
        return response.Response(serializer.data)
    
    def post(self, request, food_key):
        try:
            food = models.FoodItem.objects.get(pk=food_key)
        except models.FoodItem.DoesNotExist:
            return response.Response({"error": "Food not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = serializers.ReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, food_item=food)
            return response.Response(serializer.data, status=status.HTTP_201_CREATED)
        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)