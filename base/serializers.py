from rest_framework import serializers
from .models import *
from rest_framework_simplejwt.tokens import RefreshToken



class DishtypeSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Dishtype
        fields = '__all__'


class ItemtypeSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Itemtype
        fields = '__all__'



class RestaurantSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Restaurant
        fields = '__all__'

    
    def get_user(self, obj):
        user = obj.user
        serializer = UserSerializer(user, many=False)
        return serializer.data



class ItemSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField(read_only=True)
    dish_type = serializers.SerializerMethodField(read_only=True)
    item_type = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Item
        fields = '__all__'

    def get_user(self, obj):
        user = obj.user
        serializer = RestaurantSerializer(user, many=False)
        return serializer.data

    def get_dish_type(self, obj):
        dish_type = obj.dish_type
        serializer = DishtypeSerializer(dish_type, many=False)
        return serializer.data

    def get_item_type(self, obj):
        item_type = obj.item_type
        serializer = ItemtypeSerializer(item_type, many=False)
        return serializer.data



class ItemWithRelatedSerializer(ItemSerializer):
    related = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Item
        fields = '__all__'

    def get_related(self, obj):
        related = Item.objects.filter(
            dish_type=obj.dish_type
            ).exclude(_id=obj.pk).order_by('?').select_related('user')[:4]
        ps = ItemSerializer(related, many=True)
        return ps.data


class UserSerializer(serializers.ModelSerializer):
    
    name = serializers.SerializerMethodField(read_only=True)
    _id = serializers.SerializerMethodField(read_only=True)
    isAdmin = serializers.SerializerMethodField(read_only=True)
    number = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', '_id', 'username', 'dish_type', 'email', 'name', 'isAdmin', 'number', 'first_name', 'last_name', 'city', 'card_number', 'cvv_code', 'zip_code']


    def get_name(self, obj):
        name = obj.first_name
        if name == '':
            name = obj.email

        return name
    
    def get__id(self, obj):
        return obj.id


    def get_isAdmin(self, obj):
        return obj.is_staff

    def get_number(self, obj):
        return obj.number



class UserSerializerWithToken(UserSerializer):
    token = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', '_id', 'username', 'token', 'email', 'name', 'dish_type', 'isAdmin', 'number', 'first_name', 'last_name', 'city', 'card_number', 'cvv_code', 'zip_code']

    
    def get_token(self, obj):
        token = RefreshToken.for_user(obj)
        return str(token.access_token)



class ShippingAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingAddress
        fields = '__all__'


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'



class OrderSerializer(serializers.ModelSerializer):

    orderItems = serializers.SerializerMethodField(read_only=True)
    shippingAddress = serializers.SerializerMethodField(read_only=True)
    user = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Order
        fields = '__all__'


    def get_orderItems(self, obj):
        items = obj.orderitem_set.all()
        serializer = OrderItemSerializer(items, many=True)
        return serializer.data

    def get_shippingAddress(self, obj):
        try:
            address = ShippingAddressSerializer(obj.shippingaddress, many=False).data
        except:
            address = False

        return address

    def get_user(self, obj):
        user = obj.user
        serializer = UserSerializer(user, many=False)
        return serializer.data