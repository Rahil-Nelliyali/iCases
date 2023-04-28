from .models import Cart, CartItem
from .views import _cart_id



def counter(request):
  cart_count = 0
  if 'admin' in request.path:
    return {}
  else:
    try:
      cart = Cart.objects.filter(cart_id=_cart_id(request))
      if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(user=request.user)
      else:
        cart_items = CartItem.objects.filter(cart=cart[:1])
      
      for cart_item in cart_items:
        cart_count += cart_item.quantity
    
    except Cart.DoesNotExist:
      cart_count=0
      
  return dict(cart_count=cart_count)

def total(request):
  cart_total = 0
  if 'admin' in request.path:
    return()
  else:
    try:
      cart = Cart.objects.filter(cart_id=_cart_id(request))
      if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(user=request.user)
      else:
        cart_items = CartItem.objects.filter(cart=cart[:1])
      
      for cart_item in cart_items:
        cart_total += int(cart_item.product.offer_price())*int(cart_item.quantity)
            
    except Cart.DoesNotExist:
      cart_total=0
      
  return dict(cart_total=cart_total)