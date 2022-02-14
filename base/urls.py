from os import name
from django.urls import path
from base import views

urlpatterns = [
     path('register/', views.registerUser, name='register'),
     path('login/', views.MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
     path('restaurants/', views.restaurant, name="restaurants"),
     path('profile/update/', views.updateUserProfile, name="user-profile-update"),
     path('items/', views.getItems, name="items"),
     path('items/<str:pk>', views.getItem, name="item"),
      path('order/add/', views.addOrderItems, name='orders-add'),
     path('myorders', views.getMyOrders, name='myorders'),
     path('allorders', views.getOrders, name='orders'),
     path('order/<str:pk>/', views.getOrderById, name='user-order'),
     path('order/<str:pk>/pay', views.updateOrderToPaid, name='pay'),
]