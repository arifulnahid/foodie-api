from rest_framework.routers import DefaultRouter
from django.urls import path, include
from . import views

router = DefaultRouter()

router.register('cart', views.CartViewSet)
router.register('order', views.OrderViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('register/', views.CustomerRegister.as_view(), name='register'),
    path('login/', views.CustomerLogin.as_view(), name='login'),
    path('logout/', views.CustomerLogout.as_view(), name='logout'),
    path('activate/<uid64>/<token>/', views.activate, name='activate'),
]