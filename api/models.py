from django.db import models
import datetime
# Create your models here.
from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import BaseUserManager,AbstractUser

from django.core.mail import send_mail
from django.conf import settings
from ckeditor_uploader.fields import RichTextUploadingField

class custommanager(BaseUserManager):
    def _create_user(self,email,password=None,**extra_fields):
        if email is None:
            raise ValueError("email must have..")
        email=self.normalize_email(email)
        user=self.model(email=email,**extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_user(self,email,password=None,**extra_fields):
        extra_fields.setdefault('is_active',True)
        return self._create_user(email,password,**extra_fields)
    
    def create_superuser(self,email,password=None,**extra_fields):
        extra_fields.setdefault('is_staff',True)
        extra_fields.setdefault('is_active',True)
        extra_fields.setdefault('is_superuser',True)
        return self._create_user(email,password,**extra_fields)
    
class CustomUser(AbstractUser):
    username=None
    email=models.EmailField("email address",unique=True)
    age=models.IntegerField(blank=True,default=18)
    hobbie=models.CharField(max_length=100,blank=True)
    gender=models.CharField(max_length=50,blank=True)
    USERNAME_FIELD='email'
    REQUIRED_FIELDS=[]
    objects=custommanager()

class categories(models.Model):
    name=models.CharField(max_length=100)

    def __str__(self):
        return self.name

class price_range(models.Model):
    range=models.CharField(max_length=100)

import math
class product(models.Model):
    name=models.CharField(max_length=150)
    category=models.ForeignKey(categories,on_delete=models.CASCADE,null=True,blank=True)
    price=models.IntegerField()
    img=models.ImageField(upload_to='img',null=True,blank=True)
    date=models.DateField(auto_now_add=True)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    def discounted_price(self):
        discount_amount = (self.price * self.discount_percentage) / 100
        return math.floor(self.price - discount_amount)
    
    def __str__(self):
        return self.name

class contactus(models.Model):
    name=models.CharField(max_length=100)
    email=models.EmailField()
    mobile=models.CharField(max_length=100)
    subject=models.CharField(max_length=100)
    message=models.TextField()

    class Meta:
        verbose_name_plural='contactus' #aanathi model na name ni pachal s no lage admin panel ma

# class Cart(models.Model):
#     user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)  # Link cart to a user
#     created_at = models.DateTimeField(auto_now_add=True)
    
#     def __str__(self):
#         return f"Cart for {self.user}"

#     def total_price(self):
#         return sum(item.cart_product.discounted_price() * item.quantity for item in self.items.all())


class Cart(models.Model):
    # cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, related_name='items',on_delete=models.CASCADE, null=True, blank=True) 
    cart_product = models.ForeignKey(product, on_delete=models.CASCADE,default='')
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quantity} x {self.cart_product.name}"

    # def total_price(self):
    #     return self.cart_product.price * self.quantity
    
    def total_price(self):
        return sum(item.cart_product.discounted_price() * item.quantity for item in self.items.all())
    
class Order(models.Model):
    user=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    address=models.TextField()
    phone=models.CharField(max_length=10)
    pincod=models.CharField(max_length=6)
    date=models.DateField(default=datetime.datetime.today)
    razorpay_orderid=models.CharField(max_length=500,null=True,blank=True)
    razorpay_paymentid=models.CharField(max_length=500,null=True,blank=True)
    razorpay_signature=models.CharField(max_length=500,null=True,blank=True)

    ORD_STATUS_CHOICES = [
        ('Order Placed', 'Order Placed'),
        ('Processing', 'Processing'),
        ('Packaged', 'Packaged'),
        ('Shipped', 'Shipped'),
        ('Out for Delivery', 'Out for Delivery'),
        ('Cancelled', 'Cancelled'),
    ]
    status=models.CharField(max_length=100,choices=ORD_STATUS_CHOICES,default='Order Placed')

    def __str__(self):
        return self.razorpay_orderid if self.razorpay_orderid else "No Razorpay Order ID"
   
    def cancle_order(self):
        if self.status != 'CANCELLED':
            self.status='CANCELLED'
            self.save()
            if self.user.email:
                send_mail(
                    f"Your order {self.ord_product} cancelled",
                    f"Your order {self.ord_product} is cancelled.we are apologized for this.Thank you!",
                    settings.DEFAULT_FROM_EMAIL,
                    [self.user.email],
                    fail_silently=False,
                )

class order_items(models.Model):
    orderid=models.ForeignKey(Order,on_delete=models.CASCADE)
    image=models.ImageField(upload_to='order')
    ord_product=models.CharField(max_length=1000,default='')
    quantity=models.CharField(max_length=5)
    price=models.IntegerField()
    total=models.CharField(max_length=100,default='')

class blog(models.Model):
    name=models.CharField(max_length=100)
    body=RichTextUploadingField()

