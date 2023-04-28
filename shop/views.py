from django.shortcuts import redirect, render, get_object_or_404
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect, JsonResponse
from django.db.models import Q
from django.contrib import messages
from account.models import Account
from django.contrib.auth.views import PasswordResetView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.db.models import Q
from wishlist.models import WishlistItem
from shop.models import Category, Product, Sub_Category
from carts.models import Cart, CartItem

from carts.views import _cart_id

from account.models import Account as User
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.views.decorators.cache import never_cache
import pyotp
import random



from pyexpat.errors import messages
from django.shortcuts import render,redirect
from shop.models import Banner



def home(request):
    featured_categories = Sub_Category.objects.all().filter(is_featured=True)[:7]
    featured_products = Product.objects.all().filter(is_featured=True)[:6]
    off_products = Product.objects.filter(product_offer__gt=0)
    banner=Banner.objects.all()
    context = {
        'featured_categories': featured_categories,
        'featured_products': featured_products,
        'off_products':off_products,
         'banner' : banner,
    }

    return render(request, 'userapp/index.html', context)

@login_required(login_url="userLogin")
def change_password(request):
    if request.method == "POST":
        current_password = request.POST["current_password"]
        new_password = request.POST["new_password"]
        confirm_password = request.POST["confirm_password"]

        user = Account.objects.get(email__exact=request.user.email)

        if new_password == confirm_password:
            success = user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()
                # auth.logout(request)
                messages.success(request, "Password Updated Successfully.")
                return redirect("change_password")
            else:
                messages.error(request, "Your Existing Password Is Incorrect")
                return redirect("change_password")
        else:
            messages.info(request, "Password Does Not Match!")
            return redirect("change_password")

    return render(request, "userapp/changepassword.html")


def forgot_password(request):
    if request.method == 'POST':
        email = request.POST['email']
        if email == '':
            messages.error(request, "Fields can't be blank")
            return redirect('forgot_password')
        else:
            if User.objects.filter(email=email).exists():
                totp = pyotp.TOTP(settings.OTP_SECRET)
                otp = totp.now()
                msg_html = render_to_string(
                    'userapp/email.html', {'otp': otp})

                send_mail(f'Please verify your E-mail', f'Your One-Time Verification Password is {otp}', settings.EMAIL_HOST_USER, [
                    email], html_message=msg_html, fail_silently=False)

                request.session['otp'] = otp
                request.session['email'] = email
                return redirect('verify-email')
            else:
                messages.error(request, 'email does not exist')

    return render(request, 'userapp/forgotpassword.html')


def resend_otp(request):
  
      email = request.POST['email']
      
  
      if User.objects.filter(email=email).exists():
          
          totp = pyotp.TOTP(settings.OTP_SECRET)
          otp = totp.now()
          msg_html = render_to_string(
              'userapp/email.html', {'otp': otp})

          send_mail(f'Please verify your E-mail', f'Your One-Time Verification Password is {otp}', settings.EMAIL_HOST_USER, [
              email], html_message=msg_html, fail_silently=False)

          request.session['otp'] = otp
          request.session['email'] = email
          return redirect('verify-email')
    

@never_cache
def verify_email(request):
    if 'otp' not in request.session:
        return redirect('home')

    # if request.user.is_authenticated:
    #     return redirect('userDashboard')

    error = ''
    if request.method == 'POST':
        otp = request.session['otp']
        user_otp = request.POST['user_otp']

        if user_otp != '':
            email = request.session['email']

            if 'otp' in request.session and int(user_otp) == int(request.session['otp']):

                user = User.objects.get(email=email)

                return render(request, 'userapp/resetpassword.html')
            else:
                return render(request, 'userapp/verifyemail.html', {'error': 'Invalid OTP'})
    return render(request, 'userapp/verifyemail.html', {'error': error})


@never_cache
def reset_password(request):
    if 'otp' not in request.session:
        return redirect('home')



    if request.method == 'POST':
        password = request.POST.get('password')
        confirm = request.POST.get('conf-password')
        if not password or not confirm:
            messages.error(request, "Fields can't be blank")
        else:
            email = request.session['email']
            user = User.objects.get(email=email)
            user.set_password(password)
            user.save()
            del request.session['otp']
            del request.session['email']
            messages.success(request, 'Password reset successfuly')
            return redirect('userDashboard')

    return render(request, 'userapp/resetpassword.html')

def shop(request, category_slug=None, sub_category_slug=None):
  categories_shop= None
  subCategories_shop = None
  products = None
    
  if sub_category_slug != None:
    subCategories_shop = get_object_or_404(Sub_Category, slug=sub_category_slug)
    products = Product.objects.all().filter(sub_category=subCategories_shop, is_available=True)
    product_count = products.count()
    
  elif category_slug != None:
    categories_shop = get_object_or_404(Category, slug=category_slug)
    products = Product.objects.all().filter(category=categories_shop, is_available=True)
    product_count = products.count()
        
  else:
    categories_shop = Category.objects.all()
    subCategories_shop = Sub_Category.objects.all()
    products = Product.objects.all().filter(is_available=True).order_by('product_name')
    product_count = products.count()
    
  if request.method == 'POST':
    min = request.POST['minamount']
    max = request.POST['maxamount']
    min_price = min.split('₹')[1]
    max_price = max.split('₹')[1]
    products = Product.objects.all().filter(Q(price__gte=min_price),Q(price__lte=max_price),is_available=True).order_by('price')
    product_count = products.count()
    
  
  paginator = Paginator(products, 9)
  page_number = request.GET.get('page')
  page_obj = paginator.get_page(page_number)
  
    
  context = {
    'categories_shop':categories_shop,
    'subCategories_shop':subCategories_shop,
    'products':page_obj,
    'product_count':product_count
  }
  return render(request, 'shop/shop.html', context)

def product_details(request, category_slug, sub_category_slug, product_slug):
  categories = Category.objects.all()
  
  try:
    product = Product.objects.get(category__slug=category_slug, sub_category__slug=sub_category_slug, slug=product_slug)
    in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=product).exists()    
    related_products = Product.objects.filter(sub_category__slug=sub_category_slug)[:4]
   
  except Exception as e:
    raise e

  context = {
    'categories':categories,
    'product':product,
    "related_products":related_products,
    "in_cart":in_cart,
    
  }
  return render(request, 'shop/product_detail.html', context)

def save_review(request,pid):
   return JsonResponse({'bool': True,})
   


def price_change(request):
  var_value = request.GET['var_value']
  pro_id = request.GET['pid']
  product = Product.objects.get(id=pro_id)
  price = product.offer_price()
  x = var_value.split()
  var_value = int(x[0])
  pro_price = price * var_value
  return JsonResponse(
          {'success': True,
           'pro_price':pro_price,
           },
          safe=False
        )


def get_product_names(request):
  if 'term' in request.GET:
     qs = Product.objects.filter(product_name__icontains=request.GET.get('term'))
     product_names = list()
     for product in qs:
        product_names.append(product.product_name)
     return JsonResponse(product_names,safe=False)
  return render(request, 'shop/shop.html')


def search(request):
  if request.method == 'GET':
    keyword = request.GET['keyword']
    if keyword:
      products = Product.objects.order_by('-created_date').filter(Q(description__icontains=keyword) | Q(product_name__icontains=keyword))
      product_count = products.count()
      
  paginator = Paginator(products, 9)
  page_number = request.GET.get('page')
  page_obj = paginator.get_page(page_number)
      
  context = {
    'products':page_obj,
    'product_count':product_count,
  }
  return render(request, 'shop/shop.html', context)
  
def contact(request):
  return render(request, 'userapp/contact.html')

def sub_category(request):
  cat_id = request.GET['category_id']
  sub_categories = Sub_Category.objects.filter(category=cat_id).values()
  
  return JsonResponse(
          {'success': True,
           'sub_categories':list(sub_categories),
           },
          safe=False
        )


