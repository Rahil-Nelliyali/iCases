from django.db import models
from django.urls import reverse

# Create your models here.

class Category(models.Model):
  category_name = models.CharField(max_length=50, unique=True)
  slug = models.SlugField(max_length=100, unique=True)
  category_offer = models.IntegerField(default=0)
  description = models.TextField(max_length=255, blank=True)
  cat_image = models.ImageField(upload_to='photos/categories', blank=False)
  modified_at = models.DateTimeField(auto_now=True)
  
  class Meta:
        verbose_name        = 'category'
        verbose_name_plural = 'categories'

  def get_url(self):
      return reverse('products_by_category',args=[self.slug]) 
  
  def __str__(self):
    return self.category_name
  
class Sub_Category(models.Model):
  sub_category_name = models.CharField(max_length=50,unique=True)
  slug        = models.SlugField(max_length=50,unique=True)
  description      = models.TextField(max_length=300,blank=True)
  category        = models.ForeignKey(Category,on_delete=models.CASCADE)
  is_featured = models.BooleanField(default=False)
  
  class Meta:
        verbose_name        = 'sub category'
        verbose_name_plural = 'sub categories'


  def get_url(self):
        return reverse('products_by_sub_category',args=[self.category.slug, self.slug])  

  def __str__(self):
        return self.sub_category_name