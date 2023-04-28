from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import Cart, CartItem
from orders.models import Address, Coupon, UserCoupon
from shop.models import Product, Variation
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required


# Create your views here.


def _cart_id(request):
  cart = request.session.session_key
  if not cart:
    cart = request.session.create()
  return cart



def cart(request, total=0, quantity=0, cart_items=None):
  tax=0
  grand_total=0
  product_price = 0
  
  try:
    if request.user.is_authenticated:
      cart_items = CartItem.objects.filter(user = request.user, is_active=True).order_by('id')
    else:
      cart = Cart.objects.get(cart_id=_cart_id(request))
      cart_items = CartItem.objects.filter(cart=cart, is_active=True).order_by('id')
      
    for cart_item in cart_items:
      product_price = int(cart_item.product.offer_price()) 
      total += int(cart_item.product.offer_price())*int(cart_item.quantity)
      quantity += cart_item.quantity
      cart_item.price = product_price
      cart_item.save()
    tax = (5 * total)/100
    grand_total = total + tax
    grand_total = format(grand_total, '.2f')
  except ObjectDoesNotExist:
    pass
  
  context = {
    'total':total,
    'quantity':quantity,
    'cart_items':cart_items,
    'tax':tax,
    'grand_total':grand_total,
  }
  return render(request, 'shop/cart.html', context)



def add_cart(request, product_id):
  current_user = request.user
  product = Product.objects.get(id=product_id)
  if current_user.is_authenticated:
    product_variation = []
    if request.method == 'POST':
      for item in request.POST:
        key = item
        value = request.POST[key]
        
        try:
          variation = Variation.objects.get(product=product,variation_category__iexact=key, variation_value__iexact=value)
          product_variation.append(variation)
        except:
          pass
    
    is_cart_item_exists = CartItem.objects.filter(product=product, user=current_user).exists()
    if is_cart_item_exists:
      cart_item = CartItem.objects.filter(product=product, user=current_user)
      
      ex_var_list = []
      id = []
      for item in cart_item:
        existing_variation = item.variations.all()
        ex_var_list.append(list(existing_variation))
        id.append(item.id)
      
      if product_variation in ex_var_list:
        index = ex_var_list.index(product_variation)
        item_id = id[index]
        item = CartItem.objects.get(product=product, id=item_id)
        item.quantity += 1
        item.save()
        
      else:
        item = CartItem.objects.create(product=product, quantity=1, user=current_user)
        if len(product_variation) > 0:
          item.variations.clear()
          item.variations.add(*product_variation)
          
        item.save()
    else:
      cart_item = CartItem.objects.create(
        product=product,
        quantity = 1,
        user = current_user,
      )
      if len(product_variation) > 0:
        cart_item.variations.clear()
        cart_item.variations.add(*product_variation)
      cart_item.save()
      
    return redirect('cart')
  
  # if user is not authenticated
  else:
    product_variation = []
    if request.method == 'POST':
      for item in request.POST:
        key = item
        value = request.POST[key]
        
        try:
          variation = Variation.objects.get(product=product,variation_category__iexact=key, variation_value__iexact=value)
          product_variation.append(variation)
        except:
          pass
      
    try:
      cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
      cart = Cart.objects.create(cart_id=_cart_id(request))
    
    cart.save()
    
    is_cart_item_exists = CartItem.objects.filter(product=product, cart=cart).exists()
    if is_cart_item_exists:
      cart_item = CartItem.objects.filter(product=product, cart=cart)
      
      ex_var_list = []
      id = []
      for item in cart_item:
        existing_variation = item.variations.all()
        ex_var_list.append(list(existing_variation))
        id.append(item.id)
      
      if product_variation in ex_var_list:
        index = ex_var_list.index(product_variation)
        item_id = id[index]
        item = CartItem.objects.get(product=product, id=item_id)
        item.quantity += 1
        item.save()
      else:
        item = CartItem.objects.create(product=product, quantity=1, cart=cart)
        if len(product_variation) > 0:
          item.variations.clear()
          item.variations.add(*product_variation)
          
        item.save()
    else:
      cart_item = CartItem.objects.create(
        product=product,
        quantity = 1,
        cart = cart,
      )
      if len(product_variation) > 0:
        cart_item.variations.clear()
        cart_item.variations.add(*product_variation)
      cart_item.save()
      
    return redirect('cart')



def remove_cart(request, product_id, cart_item_id):
  product = get_object_or_404(Product, id=product_id)
  
  try:
    if request.user.is_authenticated:
      cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
    else:
      cart = Cart.objects.get(cart_id=_cart_id(request))
      cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
    
    if cart_item.quantity > 1:
      cart_item.quantity  -= 1
      cart_item.save()
    else:
      cart_item.delete()
      
  except:
    pass
  return redirect('cart')



def decqnty(request):
  product_id = request.GET['pid']
  cart_item_id = request.GET['cid']
  
  product = get_object_or_404(Product, id=product_id)
  
  tax= 0
  grand_total = 0
  cart_count = 0
  try:
    if request.user.is_authenticated:
      cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
    else:
      cart = Cart.objects.get(cart_id=_cart_id(request))
      cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
    
    if cart_item.quantity > 1:
      cart_item.quantity  -= 1
      cart_item.save()
    else:
      cart_item.delete()
      
    sub_total = cart_item.sub_total()
        
  except:
    pass
  
  try:
    if request.user.is_authenticated:
      cart_items = CartItem.objects.filter(user = request.user, is_active=True)
    else:
      cart = Cart.objects.get(cart_id=_cart_id(request))
      cart_items = CartItem.objects.filter(cart=cart, is_active=True)
    
    for cart_item in cart_items:
      cart_count += cart_item.quantity
        
    total = 0
    for cart_item in cart_items:
      total += int(cart_item.price)*int(cart_item.quantity)
    
    print(total)
    tax = (5 * total)/100
    grand_total = total + tax
    grand_total = format(grand_total, '.2f')

  except:
    pass
  
  return JsonResponse(
          {'success': True,
           'qnty':cart_item.quantity,
           'sub_total':sub_total,
           'cart_count':cart_count,
           'total':total,
           'tax':tax,
           'grand_total':grand_total,
           },
          safe=False
        )

 
  
def incqnty(request):
  if request.method == 'POST':
    product_id = request.POST['pid']
    cart_item_id = request.POST['cid']
  
  product = get_object_or_404(Product, id=product_id)
  
  tax= 0
  grand_total = 0
  cart_count = 0
  try:
    if request.user.is_authenticated:
      cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
    else:
      cart = Cart.objects.get(cart_id=_cart_id(request))
      cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
    
    if cart_item.quantity < cart_item.product.stock:
      cart_item.quantity  += 1
      cart_item.save()
      
    sub_total = cart_item.sub_total()
        
  except:
    pass
  
  try:
    if request.user.is_authenticated:
      cart_items = CartItem.objects.filter(user = request.user, is_active=True)
    else:
      cart = Cart.objects.get(cart_id=_cart_id(request))
      cart_items = CartItem.objects.filter(cart=cart, is_active=True)
      
    for cart_item in cart_items:
      cart_count += cart_item.quantity
        
    total = 0
    
    for cart_item in cart_items:
      total += int(cart_item.price)*int(cart_item.quantity)
       
    tax = (5 * total)/100
    grand_total = total + tax
    grand_total = format(grand_total, '.2f')

  except:
    pass
  
  return JsonResponse(
          {'success': True,
           'qnty':cart_item.quantity,
           'sub_total':sub_total,
           'cart_count':cart_count,
           'total':total,
           'tax':tax,
           'grand_total':grand_total,
           },
          safe=False
        )

def remove_cart_item(request, product_id, cart_item_id):
  product = get_object_or_404(Product, id=product_id)
  
  if request.user.is_authenticated:
    cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
  else:
    cart = Cart.objects.get(cart_id=_cart_id(request))
    cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
  cart_item.delete()
  return redirect('cart')

@login_required(login_url = 'userLogin')
def checkout(request, total=0, quantity=0, cart_items=None):
  tax=0
  grand_total=0
  address = Address.objects.filter(user = request.user)
  
  try:
    if request.user.is_authenticated:
      cart_items = CartItem.objects.filter(user = request.user, is_active=True)
    else:
      cart = Cart.objects.get(cart_id=_cart_id(request))
      cart_items = CartItem.objects.filter(cart=cart, is_active=True)

    for cart_item in cart_items:
      total += int(cart_item.price)*int(cart_item.quantity)
      quantity += cart_item.quantity
    tax = (5 * total)/100
    grand_total = total + tax
    grand_total = format(grand_total, '.2f')
  except ObjectDoesNotExist:
    pass
  
  coupons = Coupon.objects.filter(active = True)

  for item in coupons:
    try:
        coupon = UserCoupon.objects.get(user = request.user,coupon = item)
    except:
        coupon = UserCoupon()
        coupon.user = request.user
        coupon.coupon = item
        coupon.save() 


  coupons = UserCoupon.objects.filter(user = request.user, used=False)
  
  context = {
    'address':address,
    'total':total,
    'quantity':quantity,
    'cart_items':cart_items,
    'tax':tax,
    'grand_total':grand_total,
    'coupons':coupons,
  }
  return render(request, 'shop/checkout.html', context)