from django.urls import path
from . import views
from .api_views import ProductListAPI, ProductDetailAPI, CartItemListAPI, OrderListAPI

urlpatterns = [
    path ('',views.index_view, name='index'),
    path('profile/', views.user_profile, name='user_profile'),
    path('product/<int:pk>/', views.product_detail_view, name='product_detail'),
    path('add_to_cart/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_view, name='cart'),
    path('checkout/', views.checkout_view, name='checkout'),
    # api endpoints
      path('api/products/', ProductListAPI.as_view(), name='api_products'),
    path('api/products/<int:pk>/', ProductDetailAPI.as_view(), name='api_product_detail'),
    path('/api/cart/', CartItemListAPI.as_view(), name='api_cart'),
    path('api/orders/', OrderListAPI.as_view(), name='api_orders'),

    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]
