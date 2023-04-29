import datetime
from multiprocessing import context
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from .forms import UserForm
from multiprocessing import context
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
import random
from twilio.rest import Client
from django.views.decorators.cache import never_cache
from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Account
from .forms import RegistrationForm, UserForm
from django.contrib import messages, auth

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from requests.utils import urlparse
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from .models import Account
from .forms import RegistrationForm, UserForm, AddressForm
from django.contrib import messages, auth
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from requests.utils import urlparse

from carts.views import _cart_id, add_cart
from carts.models import Cart, CartItem
from orders.models import Order, OrderProduct, Address
from .models import Account as User


from account.models import Account as User
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.views.decorators.cache import never_cache
import pyotp
import random


#user registration
def register(request):
  if request.user.is_authenticated:
    return redirect('home')
  
  if request.method == 'POST':
    form = RegistrationForm(request.POST)
    if form.is_valid():
      first_name = form.cleaned_data['first_name']
      last_name = form.cleaned_data['last_name']
      email = form.cleaned_data['email']
      phone_number = form.cleaned_data['phone_number']
      password = form.cleaned_data['password']
           
      user = Account.objects.create_user(first_name=first_name, last_name=last_name, email=email, phone_number=phone_number, password=password)
      user.save()
      
      if user.is_active:
        messages.success(request, 'Phone verified')
        return redirect('login')
      else:
        totp = pyotp.TOTP(settings.OTP_SECRET)
        otp = totp.now()
        msg_html = render_to_string(
            'userapp/email.html', {'otp': otp})

        send_mail(f'Please verify your E-mail', f'Your One-Time Verification Password is {otp}', settings.EMAIL_HOST_USER, [
            email], html_message=msg_html, fail_silently=False)

        request.session['otp'] = otp
        request.session['email'] = email
        return redirect('verify-otp')
  else:    
    form = RegistrationForm()
  context = {
    'form': form
  }
  
  return render (request, 'userapp/usersignup.html', context)


# def send_otp(request, phone_number):


#     TWILIO_AUTH_TOKEN = '8457debf79e3cc663946ab44bf0e1b20'
#     TWILIO_ACCOUNT_SID = 'ACc4d659a3c458fa783e6f63f20e3f6dff'
#     TWILIO_PHONE_NUMBER = '+15074488476'
#     otp = random.randint(1000, 9999)
#     request.session['otp'] = otp
#     client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
#     message = client.messages.create(
#         body=f"Your OTP is {otp}",
#         from_=TWILIO_PHONE_NUMBER,
#         to=('+91{}'.format(phone_number))
#     )
#     print(message)


def resend_otp(request, phone_number):
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
        return redirect('verify-otp')

@never_cache
def verify_otp(request):
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
                user.is_active = True
                user.save()
                del request.session['otp']
                del request.session['email']
                messages.success(
                    request, 'Phone verified, please login to continue')
                return redirect('userLogin')
            else:
               return render(request, 'userapp/otpverification.html', {'error': 'Invalid OTP'})
    return render(request, 'userapp/otpverification.html', {'error': error})



@never_cache
def userLogin(request):
  if request.user.is_authenticated:
    return redirect('home')
  
  if request.method == 'POST':
    email = request.POST['email']
    password = request.POST['password']
    user = auth.authenticate(email=email, password=password)

    if user is not None:   # and user.is_superadmin==False:
      auth.login(request,user)      # login without otp
      
    #   url = request.META.get('HTTP_REFERER')
      
    #   try:
    #     query = urlparse(url).query
    #     params = dict(x.split('=') for x in query.split('&'))
    #     if 'next' in params:
    #       nextPage = params['next']
    #       return JsonResponse(
    #           {'success': True,
    #            'url':nextPage,},
    #           safe=False
    #         )
    #   except:
    #     return JsonResponse(
    #       {'success': True,
    #        'url':'/',},
    #       safe=False
    #     )
    # else:
    #   return JsonResponse(
    #     {'success':False},
    #     safe=False
    #   )
      # messages.success(request, 'You are now logged in.')
      return redirect('home')    
    else:
      messages.error(request, 'Invalid credentials')
      return redirect('userLogin')
  # form = AuthenticationForm() 
  return render (request, 'userapp/userlogin.html')

@never_cache
def otpLogin(request):
  if request.user.is_authenticated:
      return redirect('home')
  
  if request.method == 'POST':
    phone_number = request.POST['phone_number']
    request.session['phone_number'] = phone_number
    return redirect('verify-otp')
    
  else:
    return render(request, 'userapp/otploginpage.html')
  

def otpVerification(request):
  if request.user.is_authenticated:
    return redirect('home')
  
  phone_number = request.session['phone_number']
  
  if request.method == 'POST':
    
    user = Account.objects.get(phone_number=phone_number)
    try:
      check_otp = request.POST.get('otp')
      if not check_otp:
        raise e
    except Exception as e:
      messages.error(request, 'Please type in your OTP!!!')
      return redirect('otpVerification')
    
    # check = verify_otp(phone_number, check_otp)
    
    # if check:
      if user.is_active:
        auth.login(request, user)
        request.session['email'] = user.email
        return redirect('home')
      
      else:
        user.is_active = True
        user.save()
        messages.success(request, 'Account Verified.')
        return redirect('userLogin')
    
    else:
      messages.error(request, 'Invalid OTP!!!')
      return redirect('otpVerification')
    
  context = {
    'phone_number':phone_number
  }
  return render(request, 'userapp/otpverification.html', context)



@login_required(login_url = 'userLogin')
@never_cache
def userLogout(request):
  auth.logout(request)
  messages.success(request, "You are logged out.")
  return redirect('userLogin')


@login_required(login_url = 'userLogin')
def userDashboard(request):
    orders = Order.objects.order_by('-created_at').filter(user_id= request.user.id, is_ordered= True)
    orders_count = orders.count()
    context = {
        'orders_count':orders_count
    }
    return render(request, 'userapp/userprofile.html', context)


@login_required(login_url='userLogin')
def myOrders(request):
    orders = Order.objects.filter(user=request.user,is_ordered=True).order_by('-created_at')
    
    paginator = Paginator(orders, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'orders':page_obj
    }

    return render(request,'userapp/myorders.html',context)

@login_required(login_url='userLogin') 
def orderDetails(request,order_id):
    order_details = OrderProduct.objects.filter(order__order_number=order_id)
    order = Order.objects.get(order_number=order_id)
    subtotal = 0
    for i in order_details:
        subtotal += i.product_price * i.quantity
        
    context = {
        'order_details':order_details,
        'order':order,
        'subtotal':subtotal    
    }

    return render(request,'userapp/orderdetails.html',context)


@login_required(login_url='userLogin') 
@never_cache
def editProfile(request):
  if request.method =='POST':
    form = UserForm(request.POST,instance=request.user)
    if form.is_valid():
      form.save()
      messages.success(request,'Your Profile Updated Successfully ')
      return redirect ('userDashboard')

  else:
      form = UserForm(instance=request.user)

  context = {
        'form':form
    } 

  return render(request,'userapp/editprofile.html', context)

@login_required(login_url='userLogin') 
def myAddress(request):
  current_user = request.user
  address = Address.objects.filter(user=current_user)
  
  context = {
    'address':address,
  }
  return render(request, 'userapp/myaddress.html', context)

@login_required(login_url='userLogin')
@never_cache
def add_address(request):
    if request.method == 'POST':
        form = AddressForm(request.POST,request.FILES,)
        if form.is_valid():
            print('form is valid')
            detail = Address()
            detail.user = request.user
            detail.first_name =form.cleaned_data['first_name']
            detail.last_name = form.cleaned_data['last_name']
            detail.phone =  form.cleaned_data['phone']
            detail.email =  form.cleaned_data['email']
            detail.address_line1 =  form.cleaned_data['address_line1']
            detail.address_line2  = form.cleaned_data['address_line2']
            detail.district =  form.cleaned_data['district']
            detail.state =  form.cleaned_data['state']
            detail.city =  form.cleaned_data['city']
            detail.pincode =  form.cleaned_data['pincode']
            detail.save()
            
            if '/cart/checkout/' in request.GET:
                return redirect('checkout')
            else:
                return redirect('myAddress')
            
        else:
            messages.success(request,'Form is Not valid')
            return redirect('myAddress')
    else:
        form = AddressForm()
        context={
            'form':form
        }    
    return render(request,'userapp/addaddress.html',context)
  
@login_required(login_url='userLogin')
@never_cache
def edit_address(request, id):
  address = Address.objects.get(id=id)
  if request.method == 'POST':
    form = AddressForm(request.POST, instance=address)
    if form.is_valid():
      form.save()
      messages.success(request , 'Address Updated Successfully')
      return redirect('myAddress')
    else:
      messages.error(request , 'Invalid Inputs!!!')
      return redirect('myAddress')
  else:
      form = AddressForm(instance=address)
      
  context = {
            'form' : form,
        }
  return render(request , 'userapp/editaddress.html' , context)

@login_required(login_url='userLogin')
@never_cache
def delete_address(request,id):
    address=Address.objects.get(id = id)
    messages.success(request,"Address Deleted")
    address.delete()
    print('address deleted')
    return redirect('myAddress')




