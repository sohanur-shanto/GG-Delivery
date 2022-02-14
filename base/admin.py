from django.contrib import admin
from import_export import fields, resources
from .models import *
from django.contrib.admin import SimpleListFilter



class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'number', 'first_name', 'last_name', 'city', 'card_number', 'cvv_code', 'zip_code')


class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'countInStock', 'createdAt')
    list_filter = ['name', 'countInStock', 'createdAt']



class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'order', 'qty', 'get_order', 'get_payment_status')

    def get_order(self, obj):
        return obj.order.isPaid

    def get_payment_status(self, obj):
        return obj.order.status
    
    get_payment_status.admin_order_field = 'order'
    get_payment_status.short_description = 'Payment Status'

    get_order.admin_order_field = 'order'
    get_order.short_description = 'Paid ?'



class OrderAdmin(admin.ModelAdmin):
    list_display = ('_id', 'user', 'totalPrice', 'isPaid', 'status', 'paidAt', 'orderStatus', 'createdAt')
    list_filter = ['_id', 'user', 'isPaid', 'status', 'orderStatus', 'paidAt', 'createdAt']
  


admin.site.register(Order, OrderAdmin)


class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = ('address', 'order')


admin.site.register(OrderItem, OrderItemAdmin)
admin.site.register(ShippingAddress, ShippingAddressAdmin)
admin.site.register(Restaurant)
admin.site.register(Company)
admin.site.register(Dishtype)
admin.site.register(Itemtype)
admin.site.register(Item, ItemAdmin)
admin.site.register(CustomUser, CustomUserAdmin)