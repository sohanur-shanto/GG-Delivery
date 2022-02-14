from django.db.models import manager
from django.shortcuts import render
from django.http import JsonResponse
from rest_framework import serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib.auth.hashers import make_password
from rest_framework.response import Response
from base.models import *
from base.serializers import *
from rest_framework import status
from .filters import ItemFilter
from rest_framework.generics import ListAPIView
from . models import *
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
import random
from django.db.models import Q



class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    
    def validate(self, attrs):
        data = super().validate(attrs)

        serializer = UserSerializerWithToken(self.user).data

        for k, v in serializer.items():
            data[k] = v

        return data



class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer



@api_view(['POST'])
def registerUser(request):
    data = request.data

    keyword = data['city']

    restaurant = Restaurant.objects.filter(city__iexact=keyword)

    if len(restaurant) < 1:
        company = Company.objects.create(
            company_city = data['city'],
            company_name = data['company_name'],
            employee_total = data['employee_total'],
            requested = 1,
        )
    
    user = CustomUser.objects.create(
            email = data['email'],
            username = data['username'],
            first_name = data['first_name'],
            last_name = data['last_name'],
            city = data['city'],
            number = data['number'],
            password = make_password(data['password']),
            card_number = data['card_number'],
            cvv_code = data['cvv_code'],
            zip_code = data['zip_code'],
        )


    serializer = UserSerializerWithToken(user, many=False)
    return Response(serializer.data)




@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateUserProfile(request):
    user = request.user
    serializer = UserSerializerWithToken(user, many=False)
    data = request.data
    user.dish_type = data['dish_type']
    user.save()
    return Response(serializer.data)



@api_view(['GET'])
def restaurant(request):
    restaurants = Restaurant.objects.all()
    serializer = RestaurantSerializer(restaurants, many=True)
    return Response(serializer.data)



@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def getItems(request):
    # user = request.user
    
    query = request.query_params.get('keyword')
    if query == None:
        query = ''

    cuery = request.query_params.get('keyword1')
    if cuery == None:
        cuery = ''

    items = Item.objects.select_related('user').select_related('dish_type').select_related('item_type').all().filter(name__icontains=query, user__city__icontains=cuery)

    serializer = ItemSerializer(items, many=True)
    return Response(serializer.data)






# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def getItems(request):
#     user = request.user
    
#     query = request.query_params.get('keyword')
#     if query == None:
#         query = ''

#     cuery = request.query_params.get('keyword1')
#     if cuery == None:
#         cuery = ''
#         items = Item.objects.select_related('user').select_related('dish_type').select_related('item_type').all().filter(
#                     Q(name__icontains = query) | Q(user__name__icontains = query))
#     else:
#         restaurant_city = Item.objects.select_related('user').select_related('dish_type').select_related('item_type').all(
#                             ).filter(Q(user__city__iexact = cuery))
        
#         items = restaurant_city.filter(Q(name__icontains = query) | Q(user__name__icontains = query))


#     serializer = ItemSerializer(items, many=True)
#     return Response(serializer.data)



@api_view(['GET'])
def getItem(request, pk):
    item = Item.objects.get(_id=pk)
    serializer = ItemWithRelatedSerializer(item, many=False)
    return Response(serializer.data)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def addOrderItems(request):

    user = request.user
    data = request.data

    orderItems = data['orderItems']

    if orderItems and len(orderItems) == 0:
        return Response({'detail': 'No Order Items'}, status=status.HTTP_400_BAD_REQUEST)

    else:

        order = Order.objects.create(
            user=user,
            paymentMethod = data['paymentMethod'],
            taxPrice = data['taxPrice'],
            shippingPrice = data['shippingPrice'],
            totalPrice = data['totalPrice']
        )

        shipping = ShippingAddress.objects.create(
            order=order,
            address= data['shippingAddress']['address'],
            city= data['shippingAddress']['address'],
            postalCode = data['shippingAddress']['postalCode'],
            number = data['shippingAddress']['number'],

        )

        for i in orderItems:
            product = Item.objects.get(_id=i['item'])

            item = OrderItem.objects.create(
                item=product,
                order=order,
                name=product.name,
                qty=i['qty'],
                price=i['price'],
                image=product.image.url,
            )


            product.countInStock -= int(item.qty)
            product.save()

        serializer = OrderSerializer(order, many=False)
        return Response(serializer.data)
        




@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getOrderById(request, pk):
    user = request.user
    try:

        order = Order.objects.get(_id=pk)
        if user.is_staff or order.user == user:
            serializer = OrderSerializer(order, many=False)
            return Response(serializer.data)
            
        else:
            Response({'detail': 'Not Authorized to view this order'}, status=status.HTTP_400_BAD_REQUEST)

    except:
        return Response({'detail': 'Order does not exist'}, status=status.HTTP_400_BAD_REQUEST)




@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getMyOrders(request):
    user = request.user
    orders = user.order_set.all().order_by('-createdAt')
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)




@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateOrderToPaid(request, pk):
    order = Order.objects.get(_id=pk)
    DONE = 'DONE'
    order.isPaid = True
    order.paidAt = datetime.now()
    s = order.paidAt
    print(s)
    order.status = DONE
    order.save()
    return Response('Order was paid')



@api_view(['GET'])
@permission_classes([IsAdminUser])
def getOrders(request):
    orders = Order.objects.all().order_by('-createdAt')
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data) 
    
    


