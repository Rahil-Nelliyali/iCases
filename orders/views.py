from django.shortcuts import render, redirect
import datetime
from carts.models import CartItem
from .models import Order, Address, Payment, OrderProduct, Coupon, UserCoupon
import json
from shop.models import Product
from django.http import HttpResponse, JsonResponse
from django.conf import settings
import razorpay
import pytz
from datetime import datetime

from decimal import Decimal
from django.contrib import messages

# Create your views here.
client =razorpay.Client(auth=(settings.RAZORPAY_ID,settings.RAZORPAY_KEY))

def place_order(request, total=0, quantity=0):
  current_user = request.user
  
  cart_items = CartItem.objects.filter(user=current_user)
  cart_count = cart_items.count()
  if cart_count <= 0:
    return redirect('shop')
  
  grand_total = 0
  tax = 0
  for cart_item in cart_items:
    total += (cart_item.price * cart_item.quantity)
    quantity += cart_item.quantity
    
  tax = (5 * total)/100
  coupon_discount=0
  grand_total = total + tax
  grand_total = format(grand_total, '.2f')
  
  if request.method == 'POST':
      coupon_code = request.POST['coupon']
      id = request.POST['flexRadioDefault']
      address  = Address.objects.get(user = request.user,id = id)
      data = Order()
      data.user = current_user
      data.first_name = address.first_name
      data.last_name = address.last_name
      data.phone = address.phone
      data.email = address.email
      data.address_line1 = address.address_line1
      data.address_line2 = address.address_line2
      data.state = address.state
      data.district = address.district
      data.city = address.city
      data.pincode = address.pincode
      data.order_note = address.order_note
      data.order_total = grand_total
      data.tax = tax
      data.ip = request.META.get('REMOTE_ADDR')
      data.save()
      
      # Set the timezone to Indian Standard Time
      ist = pytz.timezone('Asia/Kolkata')

      # Get the current time in IST
      current_time = datetime.now(ist)

      # Extract the year, month, and day from the current time
      yr = int(current_time.strftime('%Y'))
      mt = int(current_time.strftime('%m'))
      dt = int(current_time.strftime('%d'))

      current_date = current_time.strftime('%Y%m%d')

      order_number = current_date + str(data.id)
      data.order_number = order_number
      data.save()
      
      try:
        instance = UserCoupon.objects.get(user = request.user ,coupon__code = coupon_code)
        
        if float(grand_total) >= float(instance.coupon.min_value):
          coupon_discount = ((float(grand_total) * float(instance.coupon.discount))/100)
          grand_total = float(grand_total) - coupon_discount
          grand_total = format(grand_total, '.2f')
          coupon_discount = format(coupon_discount, '.2f')
          
        data.order_total = grand_total
        data.order_discount = coupon_discount
        data.save()
        
      except:
        pass
      
      order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
      context = {
        'order':order,
        'cart_items':cart_items,
        'total':total,
        'tax':tax,
        'coupon_discount':coupon_discount,
        'grand_total':grand_total,
        'order_number':order_number,
      }
      return render(request, 'orders/payment.html', context)
  else:
      return redirect('checkout')
    
def payments(request):
  
    body = json.loads(request.body)
    
    order = Order.objects.get(user = request.user, is_ordered = False, order_number = body['orderID'])
    payment = Payment(
        user = request.user,
        payment_id = body['transID'],
        order_id = order.order_number,
        payment_method = body['paymode'],
        amount_paid = order.order_total,
        status = True
    )
    payment.save()
    order.payment = payment
    order.is_ordered = True
    order.save()
    
    
    cart_items = CartItem.objects.filter(user = request.user)

    for cart_item in cart_items:
        order_product =  OrderProduct()
        order_product.order_id = order.id
        order_product.payment = payment
        order_product.user_id =  request.user.id
        order_product.product_id = cart_item.product_id
        order_product.quantity =  cart_item.quantity
        order_product.product_price = cart_item.price
        order_product.ordered = True
        order_product.save()
        
        cart_item = CartItem.objects.get(id=cart_item.id)
        product_variation = cart_item.variations.all()
        order_product = OrderProduct.objects.get(id=order_product.id)
        order_product.variations.set(product_variation)
        order_product.save()

        product = Product.objects.get( id = cart_item.product_id)
        product.stock -= cart_item.quantity
        product.save()
    
    #clear cart
    CartItem.objects.filter(user = request.user).delete()
    
    
    #send order number and Transaction id to Web page using 
      
    data = {
        'order_number': order.order_number,
        'transID':payment.payment_id
        }
    return JsonResponse(data)
  
def payments_completed(request):
    order_number = request.GET.get('order_number')
    transID = request.GET.get('payment_id')
    try:
        order = Order.objects.get(order_number = order_number)
        ordered_products = OrderProduct.objects.filter(order_id=order.id)

        subtotal = 0
        for i in ordered_products:
            subtotal += i.product_price * i.quantity

        payment = Payment.objects.get(payment_id=transID)

        context = {
            'order': order,
            'ordered_products': ordered_products,
            'order_number': order.order_number,
            'transID': payment.payment_id,
            'payment': payment,
            'subtotal': subtotal,
        }
        return render(request, 'orders/payment-success.html', context)
    except (Payment.DoesNotExist, Order.DoesNotExist):
        return redirect('home')

def cash_on_delivery(request,id):
    # Move cart item to ordered product table
    try:
        order = Order.objects.get(user = request.user, is_ordered = False, order_number = id)
        cart_items = CartItem.objects.filter(user = request.user)
        order.is_ordered = True
        payment = Payment(
            user = request.user,
            payment_id = order.order_number,
            order_id = order.order_number,
            payment_method = 'Cash On Delivery', 
            amount_paid = order.order_total,
            status = False
        )
        payment.save()
        order.payment = payment
        order.is_ordered = True
        order.save()
        for cart_item in cart_items:
            order_product =  OrderProduct()
            order_product.order_id = order.id

            order_product.user_id =  request.user.id
            order_product.product_id = cart_item.product_id
            order_product.quantity =  cart_item.quantity
            order_product.product_price = cart_item.sub_total()
            order_product.ordered = True
            order_product.save()
            
            cart_item = CartItem.objects.get(id=cart_item.id)
            product_variation = cart_item.variations.all()
            order_product = OrderProduct.objects.get(id=order_product.id)
            order_product.variations.set(product_variation)
            order_product.save()
            
        #Reduce Quantity of product
        
            product = Product.objects.get( id = cart_item.product_id)
            product.stock -= cart_item.quantity
            product.save()

        #clear cart
        CartItem.objects.filter(user = request.user).delete()
        ordered_products = OrderProduct.objects.filter(order_id=order.id)
        
        subtotal = 0
        for i in ordered_products:
            subtotal += i.product_price * i.quantity
        
        context ={
          'order':order,
          'ordered_products':ordered_products,
          'payment':payment,
          'subtotal':subtotal,
             }
        return render(request,'orders/cod_success.html',context)
    except:
      return redirect('home')
    
def cancel_order(request,id):
    if request.user.is_superadmin:
      order = Order.objects.get(order_number = id)
    else:
      order = Order.objects.get(order_number = id,user = request.user)

    payment = Payment.objects.get(order_id = order.order_number)

    if payment.payment_method=="Cash On Delivery":
      order.status = "Cancelled"
      order.save()
      payment.status = "Cancelled"
      payment.save()
    else:
       # Initialize the Razorpay client with your API keys
            # client =razorpay.Client(auth=(settings.RAZORPAY_ID,settings.RAZORPAY_KEY))

            # Retrieve the payment ID and amount from your Django order object
            payment_id = order.payment.payment_id
            # amount in paise (e.g. Rs. 10.00 = 1000 paise)
            amount = Decimal(order.payment.amount_paid)*100

            # Check if the payment has been captured and is refundable
            payment = client.payment.fetch(payment_id)
            if payment['status'] != 'captured':
                messages.error(request, 'Payment cannot be refunded')

            else:

                # Create a refund object using the Razorpay API
                refund_data = {
                    'payment_id': payment_id,
                    'amount': str(amount),
                    'notes': {'reason': 'User cancelled order'}
                }
                refund = client.refund.create(data=refund_data)

                # Update the status of the order in your Django application
                order.status = 'Cancelled'
                order.save()
               
                # Monitor the status of the refund using the Razorpay API
                refund = client.refund.fetch(refund['id'])

               

    if request.user.is_superadmin:
      return redirect('orders')
    else:
      return redirect('orderDetails', id)
    
def return_order(request, id):
  if request.method == 'POST':
    return_reason = request.POST['return_reason']
  print(return_reason)
  order = Order.objects.get(order_number = id,user = request.user)
  order.status = "Returned"
  order.is_returned = True
  order.return_reason = return_reason
  order.save()
  payment = Payment.objects.get(order_id = order.order_number)
  if payment.payment_method=="Cash On Delivery":
      payment.status = "Cancelled"
      payment.save()
      
  
  else:
     # Retrieve the payment ID and amount from your Django order object
            payment_id = order.payment.payment_id
            # amount in paise (e.g. Rs. 10.00 = 1000 paise)
            amount = Decimal(order.payment.amount_paid)*100

            # Check if the payment has been captured and is refundable
            payment = client.payment.fetch(payment_id)
            if payment['status'] != 'captured':
                messages.error(request, 'Payment cannot be refunded')

            else:

                # Create a refund object using the Razorpay API
                refund_data = {
                    'payment_id': payment_id,
                    'amount': str(amount),
                    'notes': {'reason': 'User cancelled order'}
                }
                refund = client.refund.create(data=refund_data)

                # Update the status of the order in your Django application
                order.status = 'Cancelled'
                order.save()
               
                refund = client.refund.fetch(refund['id'])
  return redirect('orderDetails', id)
            
     
  
  

def razorpay(request):
  
  body = json.loads(request.body)
  amount = body['amount']
      
  amount = float(amount) * 100
  
  DATA = {
    "amount": amount,
    "currency": "INR",
    "receipt": "receipt#1",
    "notes": {
        "key1": "value3",
        "key2": "value2"
    }
      }
  payment = client.order.create(data=DATA)
  return JsonResponse({
    'payment':payment,
     'payment_method' : "RazorPay"
      })


def coupon(request):
  if request.method == 'POST':
    coupon_code = request.POST['coupon']
    grand_total = request.POST['grand_total']
    coupon_discount = 0
    try:
      instance = UserCoupon.objects.get(user = request.user ,coupon__code = coupon_code)

      if float(grand_total) >= float(instance.coupon.min_value):
        coupon_discount = ((float(grand_total) * float(instance.coupon.discount))/100)
        grand_total = float(grand_total) - coupon_discount
        grand_total = format(grand_total, '.2f')
        coupon_discount = format(coupon_discount, '.2f')
        msg = 'Coupon Applied successfully'
        instance.used = True
        instance.save()
      else:
          msg='This coupon is only applicable for orders more than ₹'+ str(instance.coupon.min_value)+ '\- only!'
    except:
            msg = 'Coupon is not valid'
    response = {
               'grand_total': grand_total,
               'msg':msg,
               'coupon_discount':coupon_discount,
               'coupon_code':coupon_code,
                }

  return JsonResponse(response)


