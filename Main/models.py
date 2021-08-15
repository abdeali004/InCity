from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
import random
# Create your models here.


def user_directory_path1(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    i = random.randint(1,1000)
    ext = filename.split('.')[-1]
    return 'ProductImages/{0}{1}+.{2}'.format(instance.productId,i, ext)

def user_directory_path2(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    i = random.randint(1,1000)
    ext = filename.split('.')[-1]
    return 'ShopImages/{0}{1}+.{2}'.format(instance.username,i, ext)




class Product(models.Model):
    username = models.ForeignKey(User, on_delete=models.CASCADE)
    productId = models.CharField(max_length=50, primary_key=True)
    productName = models.CharField(max_length=100)
    typeOf = models.CharField(max_length=50)
    category = models.CharField(max_length=50)
    actualPrice = models.IntegerField(default=0)
    sellingPrice = models.IntegerField(default=0)
    description = models.TextField()
    coupon = models.CharField(max_length=50)
    image1 = models.ImageField(upload_to=user_directory_path1, height_field=None, width_field=None, max_length=None)
    image2 = models.ImageField(upload_to=user_directory_path1, height_field=None, width_field=None, max_length=None)
    image3 = models.ImageField(upload_to=user_directory_path1, height_field=None, width_field=None, max_length=None)
    stock = models.IntegerField(default=0)
    buyed = models.IntegerField(default=0)
    wishlist = models.IntegerField(default=0)
    views = models.IntegerField(default=0)
    searched = models.IntegerField(default=0)
    date = models.DateTimeField(auto_now=False, auto_now_add=True)


    def __str__(self):
        return self.productId
    

    def delete(self, *args, **kwargs):
        self.image1.delete()
        self.image2.delete()
        self.image3.delete()
        super().delete(*args, **kwargs)  # Call the "real" delete(*args, **kwargs) method.
        


class UserInfo(models.Model):
    username = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    typeOf = models.CharField(max_length=50)
    gender = models.CharField(max_length=50)
    categories = models.CharField(max_length=150)
    buyed = models.IntegerField(default=0)
    visitedSite = models.IntegerField(default=0)
    addressPrimary = models.TextField(default="")
    city = models.CharField(max_length=50,default="")
    state = models.CharField(max_length=50,default="")
    postal = models.CharField(max_length=50,default="")
    about = models.TextField(default="")
    wishlist = models.TextField(default="")
    cart = models.TextField(default="")
    shopVisited = models.TextField(default="")
    productVisited = models.TextField(default="")
    buyedProducts = models.TextField(default="")
    isNew = models.BooleanField(default=True)
    isFirstVisit = models.BooleanField(default=True)
    date = models.DateTimeField(auto_now=False, auto_now_add=True)


    def __str__(self):
        return str(self.username)


class Shop(models.Model):
    username = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    shopName = models.CharField(max_length=100)
    typeOf = models.CharField(max_length=50)
    categories = models.CharField(max_length=150)
    image1 = models.ImageField(upload_to=user_directory_path2, height_field=None, width_field=None, max_length=None)
    image2 = models.ImageField(upload_to=user_directory_path2, height_field=None, width_field=None, max_length=None)
    image3 = models.ImageField(upload_to=user_directory_path2, height_field=None, width_field=None, max_length=None)
    totalProducts = models.IntegerField(default=0)
    countId = models.IntegerField(default=1)
    productVisited = models.TextField()
    wishlisted = models.TextField()
    totalStock = models.IntegerField(default=0)
    totalSale = models.IntegerField(default=0)
    totalVisited = models.IntegerField(default=0)
    searched = models.IntegerField(default=0)
    rating = models.FloatField(default=0)
    custVoted = models.IntegerField(default=0)
    description = models.TextField(default="")
    owner = models.CharField(max_length=70)
    contact = models.CharField(max_length=20,default="")
    addressPrimary = models.TextField()
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    postal = models.CharField(max_length=50)
    date = models.DateTimeField(auto_now=False, auto_now_add=True)

    def __str__(self):
        return self.shopName
    
    def delete(self, *args, **kwargs):
        self.image1.delete()
        self.image2.delete()
        self.image3.delete()
        super().delete(*args, **kwargs)  # Call the "real" delete(*args, **kwargs) method.