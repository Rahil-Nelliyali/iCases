from django.db import models
from account.models import Account
from shop.models import Product, Variation

# Create your models here.


class Cart(models.Model):
  cart_id = models.CharField(max_length=250, blank=True)
  date_added = models.DateField(auto_now_add=True)
  
  def __str__(self):
    return self.cart_id
  
class CartItem(models.Model):
  user = models.ForeignKey(Account, on_delete=models.CASCADE, null=True)
  product = models.ForeignKey(Product, on_delete=models.CASCADE)
  variations = models.ManyToManyField(Variation, blank=True)
  cart = models.ForeignKey(Cart, on_delete=models.CASCADE, null=True)
  quantity = models.IntegerField()
  price = models.IntegerField(default=1)
  is_active = models.BooleanField(default=True)
  
  def sub_total(self):
    return int(self.price)*int(self.quantity)
  
  def __unicode__(self):
    return self.product