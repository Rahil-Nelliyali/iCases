from django.conf import settings
from django.db import models
from django.urls import reverse
from account.models import Account
from category.models import Category, Sub_Category

# Create your models here.

class Product(models.Model):
  
  UNIT = (('Piece', 'Piece'),('Combo', 'Combo'),)
  product_name = models.CharField(max_length=200, unique=True)
  slug = models.SlugField(max_length=255, unique=True)
  description = models.TextField(max_length=500, blank=True)
  price = models.IntegerField()
  product_offer = models.IntegerField(default = 0)
  unit = models.CharField(max_length=50,choices=UNIT,default='Piece')
  image_1 = models.ImageField(upload_to='photos/products', blank=False)
  image_2 = models.ImageField(upload_to='photos/products', blank=True)
  image_3 = models.ImageField(upload_to='photos/products', blank=True)
  image_4 = models.ImageField(upload_to='photos/products', blank=True)
  stock = models.IntegerField()
  is_available = models.BooleanField(default=True)
  is_featured = models.BooleanField(default=False)
  category = models.ForeignKey(Category, on_delete=models.CASCADE)
  sub_category = models.ForeignKey(Sub_Category, on_delete=models.CASCADE)
  created_date = models.DateTimeField(auto_now_add=True)
  modified_date = models.DateTimeField(auto_now=True)
  users_wishlist     =models.ManyToManyField(settings.AUTH_USER_MODEL,related_name='users_wishlist',blank=True)
  
  def get_url(self):
    return reverse('product_details', args=[self.category.slug, self.sub_category.slug, self.slug])
  
  def __str__(self):
    return self.product_name
  
  def offer_price(self):
    product_offer = int(self.price) - int(self.price) * int(self.product_offer) /100 
    category_offer = int(self.price) - int(self.price) * int(self.category.category_offer)/100
    if product_offer == int(self.price) and category_offer == int(self.price):
        return self.price
    if product_offer <= category_offer:
        return int(product_offer)
    else:
        return category_offer
  
class VariationManager(models.Manager):
  def sizes(self):
    return super(VariationManager, self).filter(variation_category='size', is_active=True)
  
variation_category_choice =  (
    ('size','size'),
)


class Variation(models.Model):
  product = models.ForeignKey(Product, on_delete=models.CASCADE)
  variation_category = models.CharField(max_length=100, choices=variation_category_choice)
  variation_value = models.CharField(max_length=100)
  is_active = models.BooleanField(default=True)
  created_date = models.DateTimeField(auto_now=True)
  
  objects = VariationManager()
  
  def __str__(self):
    return self.variation_value
  






#product review
RATING = (
  (1,'1'),
  (2,'2'),
  (3,'3'),
  (4,'4'),
  (5,'5'),
)
class ProductReview(models.Model):
   user = models.ForeignKey(Account, on_delete=models.CASCADE, null=True)
   product = models.ForeignKey(Product, on_delete=models.CASCADE)
   review_text = models.TextField(null=True)
   review_rating = models.CharField(choices=RATING, max_length=150)



class Banner(models.Model):
    
    banner_image =models.ImageField( upload_to='photos/banner', height_field=None, width_field=None, max_length=None,blank=True)
    
    is_selected = models.BooleanField(default=False)