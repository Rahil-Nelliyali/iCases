from .models import Product
from category.models import Sub_Category

def latest_products1(request):
  latest_products_1 = Product.objects.all().order_by('-created_date')[:3]
  return dict(latest_products_1=latest_products_1)

def latest_products2(request):
  latest_products_2 = Product.objects.all().order_by('-created_date')[3:6]
  return dict(latest_products_2=latest_products_2)

def offer_products1(request):
  offer_products = Product.objects.filter(product_offer__gt=0).order_by('-product_offer')[:3]
  return dict(offer_products1=offer_products)

def offer_products2(request):
  offer_products = Product.objects.filter(product_offer__gt=0).order_by('-product_offer')[3:6]
  return dict(offer_products2=offer_products)

def selling_products1(request):
  selling_products = Product.objects.all().order_by('stock')[:3]
  return dict(selling_products1=selling_products)

def selling_products2(request):
  selling_products = Product.objects.all().order_by('stock')[3:6]
  return dict(selling_products2=selling_products)

