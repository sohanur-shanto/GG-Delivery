from re import T
from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal
from PIL import Image, ImageDraw
from datetime import datetime, timedelta
from django.dispatch import receiver
from django.urls import reverse
from django_rest_passwordreset.signals import reset_password_token_created
from django.core.mail import send_mail
from io import BytesIO
from django.core.files import File
import qrcode
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import get_template
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.safestring import mark_safe





class Dishtype(models.Model):
    name = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return str(self.name)



class Itemtype(models.Model):
    name = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return str(self.name)


dish_type_choices = [

    ('African', 'African'),
    ('Asian', 'Asian'),
    ('American', 'American'),
    ('European', 'European'),
    
]


class CustomUser(AbstractUser):
    
    email = models.EmailField(unique=True)
    city = models.CharField(max_length=200, blank=True, null=True)
    first_name = models.CharField(max_length=200, blank=True, null=True)
    last_name = models.CharField(max_length=200, blank=True, null=True)
    number = models.CharField(max_length=200, unique=True)
    dish_type = models.CharField(max_length=220, null=True, blank=True, choices=dish_type_choices)
    card_number = models.IntegerField(blank=True, null=True)
    expires = models.DateField(auto_now_add=False, blank=True, null=True)
    cvv_code = models.IntegerField(blank=True, null=True)
    zip_code = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return str(self.username)



class Restaurant(models.Model):
    user = models.OneToOneField(CustomUser, related_name='restaurant', on_delete=models.CASCADE, null=False)
    name = models.CharField(max_length=200, blank=True, null=True)
    profile_picture = models.ImageField(null=True, blank=True)
    address = models.TextField(max_length=2000, blank=True, null=True)
    city = models.CharField(max_length=200)
    latitude = models.DecimalField(max_digits = 13, decimal_places = 7, blank=True, null=True)
    longitude = models.DecimalField(max_digits = 13, decimal_places = 7, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    createdAt = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return str(self.name)



class Item(models.Model):
    user = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    name = models.CharField(max_length=220)
    image = models.ImageField(null=True, blank=True)
    dish_type = models.ForeignKey(Dishtype, on_delete=models.CASCADE)
    item_type = models.ForeignKey(Itemtype, on_delete=models.CASCADE)
    description = models.TextField(max_length=10000)
    rating = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True)
    numReviews = models.IntegerField(null=True, blank=True, default=0)
    old_price = models.DecimalField(max_digits=11, decimal_places=2)
    discount = models.IntegerField(blank=True, null=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    countInStock = models.IntegerField(blank=True, null=True, default=0)
    createdAt = models.DateTimeField(auto_now_add=True)
    _id = models.AutoField(primary_key=True, editable=False)
    

    def save(self, *args, **kwargs):
        self.price = Decimal(self.old_price * (100 - self.discount) / 100)
        return super(Item, self).save(*args, **kwargs)
    

    class Meta:
        ordering = ['-createdAt']


    def __str__(self):
        return self.name





class Order(models.Model):
    
    PENDING_PAYMENT = 'Pending Payment'
    ON_HOLD = 'On Hold'

    status_choices = [

        ('Cancel', 'Cancel'),
        ('Pending Payment', 'Pending Payment'),
        ('On Hold', 'On Hold'),
        ('Waiting For Payment', 'Waiting For Payment'),
        ('Processing', 'Processing'),
        ('Done', 'Done'),

    ]

    orderstatus_choices = [

        ('Cancel', 'Cancel'),
        ('Pending Payment', 'Pending Payment'),
        ('On Hold', 'On Hold'),
        ('Waiting For Payment', 'Waiting For Payment'),
        ('Processing', 'Processing'),
        ('Done', 'Done'),

    ]

    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    paymentMethod = models.CharField(max_length=200, null=True, blank=True)
    taxPrice = models.DecimalField(max_digits=11, decimal_places=2, null=True, blank=True)
    shippingPrice = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    totalPrice = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    isPaid = models.BooleanField(default=False)
    paidAt = models.DateTimeField(auto_now_add=False, null=True, blank=True)
    isDelivered = models.BooleanField(default=False)
    createdAt = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=220, choices=status_choices, default=PENDING_PAYMENT)
    orderStatus= models.CharField(max_length=220, choices=orderstatus_choices, default=ON_HOLD, blank=True, null=True)
    qr_code = models.ImageField(upload_to='static/images', blank=True, null=True)
    _id = models.AutoField(primary_key=True, editable=False)


    def save(self, *args, **kwargs):
        n = '\n'
        qrcode_img = qrcode.make(f'Created By - {self.user.username} {n} Status - {self.status} {n} Total - {self.totalPrice} TK')
        canvas = Image.new('RGB', (440, 440), 'white')
        draw = ImageDraw.Draw(canvas)
        canvas.paste(qrcode_img)
        fname = f'qr_code-{self.user}' + '.png'
        buffer = BytesIO()
        canvas.save(buffer, 'PNG')
        self.qr_code.save(fname, File(buffer), save=False)
        canvas.close()
        super().save(*args, **kwargs)


    def __str__(self):
        return str(self._id)




class OrderItem(models.Model):
    item = models.ForeignKey(Item, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    restaurant = models.ForeignKey(Restaurant,on_delete=models.SET_NULL,null=True, related_name='restaurants')
    vendor_paid = models.BooleanField(default=False)
    name = models.CharField(max_length=200, null=True, blank=True)
    qty = models.IntegerField(null=True, blank=True, default=0)
    price = models.DecimalField(max_digits=13, decimal_places=2, null=True, blank=True)
    image = models.CharField(max_length=200, null=True, blank=True)
    _id = models.AutoField(primary_key=True, editable=False)

    def __str__(self):
        return self.name



class ShippingAddress(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, null=True, blank=True)
    address = models.CharField(max_length=220, null=True, blank=True)
    city = models.CharField(max_length=30, null=True, blank=True)
    postalCode = models.CharField(max_length=20, null=True, blank=True)
    number = models.CharField(max_length=30, null=True, blank=True)
    shippingPrice = models.DecimalField(max_digits=13, decimal_places=2, null=True, blank=True)
    _id = models.AutoField(primary_key=True, editable=False)

    def __str__(self):
        return self.address







class Company(models.Model):
    company_city = models.CharField(max_length=200)
    company_name = models.CharField(max_length=200, blank=True, null=True)
    employee_total = models.IntegerField()
    requested = models.BooleanField(default=False)


    def __str__(self):
        return str(self.company_name)





