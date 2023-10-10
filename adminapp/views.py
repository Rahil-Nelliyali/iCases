from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.cache import never_cache
from django.shortcuts import get_object_or_404
from datetime import datetime,timedelta,date
from django.db.models import Sum, Q, FloatField
from django.db.models.functions import Cast
from django.core.paginator import Paginator

from .forms import LoginForm, ProductForm, CategoryForm, SubCategoryForm, UserForm, CouponForm, VariationForm
from account.models import Account
from shop.models import Product, Variation
from category.models import Category, Sub_Category
from orders.models import Order, Payment, Coupon

from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
import xlwt


from shop.models import Banner

def admin_login(request):
    if 'email' in request.session:
        return redirect('admin_home')
    
    if request.method == 'POST':
        # form = LoginForm(request.POST)
        email = request.POST['email']
        password = request.POST['password']
        
        user = authenticate(email=email, password=password)
        
        if user is not None:
            if user.is_superadmin:
                request.session['email'] = email
                
                login(request, user)
                return redirect('admin_home')
                
            else:
                messages.error(request, 'Not Authorized!!!')
                return redirect(admin_login)
        else:
            messages.error(request, 'Invalid login credentials')
            return redirect(admin_login)
        
    form = LoginForm
    return render(request, 'adminapp/admin_login.html', {'form':form})

@staff_member_required(login_url = 'admin_login')
def admin_home(request):
    today = datetime.today()
    today_date = today.strftime("%Y-%m-%d")
    month = today.month
    year = today.strftime("%Y")
    one_week = datetime.today() - timedelta(days=7)
    order_count_in_month = Order.objects.filter(created_at__year = year,created_at__month=month, is_ordered=True).count() 
    order_count_in_day =Order.objects.filter(created_at__date = today, is_ordered=True).count()
    order_count_in_week = Order.objects.filter(created_at__gte = one_week, is_ordered=True).count()
    number_of_users  = Account.objects.filter(is_admin = False).count()
    paypal_orders = Payment.objects.filter(payment_method="PayPal",status = True).count()
    razorpay_orders = Payment.objects.filter(payment_method="RazerPay",status = True).count()
    cash_on_delivery_count = Payment.objects.filter(payment_method="Cash On Delivery",status = True).count()

    total_payment_count = paypal_orders + razorpay_orders + cash_on_delivery_count
    try:
        total_payment_amount = Payment.objects.filter(status = True).annotate(total_amount=Cast('amount_paid', FloatField())).aggregate(Sum('total_amount'))
        
    except:
        total_payment_amount=0
        
    if total_payment_amount['total_amount__sum'] :
      revenue = total_payment_amount['total_amount__sum']
      revenue = format(revenue, '.2f')
    
    else:
      revenue = 0
           
    blocked_user = Account.objects.filter(is_active = False,is_superadmin = False).count()
    unblocked_user = Account.objects.filter(is_active = True,is_superadmin = False).count()

    today_sale = Order.objects.filter(created_at__date = today_date,payment__status = True, is_ordered=True).count()
    today = today.strftime("%A")
    new_date = datetime.today() - timedelta(days = 1)
    yester_day_sale =   Order.objects.filter(created_at__date = new_date,payment__status = True, is_ordered=True).count()  
    yesterday = new_date.strftime("%A")
    new_date = new_date - timedelta(days = 1)
    day_2 = Order.objects.filter(created_at__date = new_date,payment__status = True, is_ordered=True).count()
    day_2_name = new_date.strftime("%A")
    new_date = new_date - timedelta(days = 1)
    day_3 = Order.objects.filter(created_at__date = new_date,payment__status = True, is_ordered=True).count()
    day_3_name = new_date.strftime("%A")
    new_date = new_date - timedelta(days = 1)
    day_4 = Order.objects.filter(created_at__date = new_date,payment__status = True, is_ordered=True).count()
    day_4_name = new_date.strftime("%A")
    new_date = new_date - timedelta(days = 1)
    day_5 = Order.objects.filter(created_at__date = new_date,payment__status = True, is_ordered=True).count()
    day_5_name = new_date.strftime("%A")
    #status
    ordered = Order.objects.filter(status = 'Order Confirmed', is_ordered=True).count()
    shipped = Order.objects.filter(status = "Shipped").count()
    out_of_delivery = Order.objects.filter(status ="Out for delivery").count()
    delivered = Order.objects.filter(status = "Delivered").count()
    returned = Order.objects.filter(status = "Returned").count()
    cancelled = Order.objects.filter(status = "Cancelled").count()

    context ={
        'order_count_in_month':order_count_in_month,
        'order_count_in_day':order_count_in_day,
        'order_count_in_week':order_count_in_week,
        'number_of_users':number_of_users,
        'paypal_orders':paypal_orders,
        'razorpay_orders':razorpay_orders,
        'total_payment_count':total_payment_count,
        'revenue':revenue,
        'ordered':ordered,
        'shipped':shipped,
        'out_of_delivery':out_of_delivery,
        'delivered':delivered,
        'returned':returned,
        'cancelled':cancelled,
        'cash_on_delivery_count':cash_on_delivery_count,
        'blocked_user':blocked_user,
        'unblocked_user':unblocked_user,
        'today_sale':today_sale,
        'yester_day_sale':yester_day_sale,
        'day_2':day_2,
        'day_3':day_3,
        'day_4':day_4,
        'day_5':day_5,
        'today':today,
        'yesterday':yesterday,
        'day_2_name':day_2_name,
        'day_3_name':day_3_name,
        'day_4_name':day_4_name,
        'day_5_name':day_5_name
        
    }
    return render(request, 'adminapp/admin_home.html', context)
  
    
    
@staff_member_required(login_url = 'admin_login')
def admin_logout(request):
    if 'email' in request.session:
        request.session.flush()
    logout(request)
    messages.success(request, 'Logged out successfully.')
    return redirect('admin_login')

@staff_member_required(login_url = 'admin_login')
def user_manage(request):
    users=Account.objects.all().filter(is_superadmin=False).order_by('-id')
    paginator=Paginator(users,10)
    page=request.GET.get('page')
    paged_user_list=paginator.get_page(page)
    return render(request,'adminapp/user_manage.html',{
        'users':paged_user_list
    })


@staff_member_required(login_url = 'admin_login')
def blockUser(request, id):
    users = Account.objects.get(id=id)
    if users.is_active:
        users.is_active = False
        users.save()

    else:
         users.is_active = True
         users.save()

    return redirect('user_manage')


# Category Management

@staff_member_required(login_url = 'admin_login')
def categories(request):
  categories = Category.objects.all().order_by('id')
  
  paginator = Paginator(categories, 10)
  page_number = request.GET.get('page')
  page_obj = paginator.get_page(page_number)
  
  context = {
    'categories':page_obj
  }
  return render(request, 'adminapp/categories.html', context)

@staff_member_required(login_url = 'admin_login')
def addCategory(request):
  if request.method == 'POST':
    form = CategoryForm(request.POST, request.FILES)
    if form.is_valid():
      form.save()
      messages.success(request, 'Category added successfully.')
      return redirect('categories')
    else:
      messages.error(request, 'Invalid input!!!')
      return redirect('addCategory')
  else:
    form = CategoryForm()
    context = {
      'form':form,
    }
    return render(request, 'adminapp/addcategory.html', context)
  
@staff_member_required(login_url = 'admin_login')
def editCategory(request, slug):
  category = Category.objects.get(slug=slug)
  
  if request.method == 'POST':
    form = CategoryForm(request.POST, request.FILES, instance=category)
    
    if form.is_valid():
      form.save()
      messages.success(request, 'Category edited successfully.')
      return redirect('categories')
    else:
      messages.error(request, 'Invalid input')
      return redirect('editCategory', slug)
      
  form =   CategoryForm(instance=category)
  context = {
    'form':form,
    'category':category,
  }
  return render(request, 'adminapp/editcategory.html', context)
  
@staff_member_required(login_url = 'admin_login')  
def deleteCategory(request, slug):
  category = Category.objects.get(slug=slug)
  category.delete()
  messages.success(request, 'Category deleted successfully.')
  return redirect('categories')



# sub category management

@staff_member_required(login_url = 'admin_login')
def subCategories(request, category_slug):
  subCategories = Sub_Category.objects.all().filter(category__slug=category_slug)
  context = {
    'subCategories':subCategories,
    'category_slug':category_slug,
  }
  return render(request, 'adminapp/subcategories.html', context)

@staff_member_required(login_url = 'admin_login')
def addSubCategory(request, category_slug):
  category = Category.objects.get(slug=category_slug)
  if request.method == 'POST':
    form = SubCategoryForm(request.POST, request.FILES)
    if form.is_valid():
      form.save()
      messages.success(request, 'Sub Category added successfully.')
      return redirect('subCategories', category_slug)
    else:
      messages.error(request, 'Invalid input!!!')
      return redirect('addSubCategory', category_slug)
  else:
    form = SubCategoryForm()
    context = {
      'form':form,
      'category':category
    }
    return render(request, 'adminapp/addsubcategory.html', context)
  
@staff_member_required(login_url = 'admin_login')
def editSubCategory(request, slug):
  subCategory = Sub_Category.objects.get(slug=slug)
  cat_slug = subCategory.category.slug
  
  if request.method == 'POST':
    form = SubCategoryForm(request.POST, request.FILES, instance=subCategory)
    
    if form.is_valid():
      form.save()
      messages.success(request, 'Category edited successfully.')
      return redirect('subCategories', cat_slug)
    else:
      messages.error(request, 'Invalid input')
      return redirect('editSubCategory')
      
  form =   SubCategoryForm(instance=subCategory)
  context = {
    'form':form,
    'subCategory':subCategory,
  }
  return render(request, 'adminapp/editsubcategory.html', context)

@staff_member_required(login_url = 'admin_login')  
def deleteSubCategory(request, slug):
  sub_category = Sub_Category.objects.get(slug=slug)
  cat_slug = sub_category.category.slug
  sub_category.delete()
  messages.success(request, 'Sub Category deleted successfully.')
  return redirect('subCategories', cat_slug)
 
 
 
# Product management
  
@staff_member_required(login_url = 'admin_login')
def products(request):
  products = Product.objects.all().order_by('-id')
  
  paginator = Paginator(products, 10)
  page_number = request.GET.get('page')
  page_obj = paginator.get_page(page_number)
  
  context = {
    'products': page_obj
  }
  return render(request, 'adminapp/products.html', context)

@staff_member_required(login_url = 'admin_login')
def addProduct(request):
  if request.method == 'POST':
    form = ProductForm(request.POST, request.FILES)
    if form.is_valid():
      form.save()
      messages.success(request, 'Product added successfully.')
      return redirect('products')
    else:
      messages.error(request, 'Invalid input!!!')
      return redirect('addProduct')
  else:
    form = ProductForm()
    context = {
      'form':form,
    }
    return render(request, 'adminapp/addproduct.html', context)

@staff_member_required(login_url = 'admin_login')
def editProduct(request, id):
  product = Product.objects.get(id=id)
  
  if request.method == 'POST':
    form = ProductForm(request.POST, request.FILES, instance=product)
    
    if form.is_valid():
      form.save()
      messages.success(request, 'Product edited successfully.')
      return redirect('products')
    else:
      messages.error(request, 'Invalid input')
      
  form =   ProductForm(instance=product)
  context = {
    'form':form,
    'product':product,
  }
  return render(request, 'adminapp/editproduct.html', context)

@staff_member_required(login_url = 'admin_login')  
def deleteProduct(request, id):
  product = Product.objects.get(id=id)
  product.delete()
  return redirect('products')


# variations

@staff_member_required(login_url= 'admin_login')
def product_variations(request):
  variations = Variation.objects.all().order_by('product')
  
  paginator = Paginator(variations, 10)
  page_number = request.GET.get('page')
  page_obj = paginator.get_page(page_number)
  
  context = {
    'variations':page_obj,
  }
  return render(request, 'adminapp/productvariations.html', context)

@staff_member_required(login_url= 'admin_login')
def delete_product_variation(request, id):
  variation = Variation.objects.get(id=id)
  variation.delete()
  messages.success(request, 'Variation deleted successfully!!!')
  return redirect('product_variations')

@staff_member_required(login_url= 'admin_login')
def edit_product_variation(request, id):
  variation = Variation.objects.get(id=id)
  
  if request.method == 'POST':
    form = VariationForm(request.POST, instance=variation)
    
    if form.is_valid():
      form.save()
      messages.success(request, 'Variation edited successfully.')
      return redirect('product_variations')
    else:
      messages.error(request, 'Invalid input')
      return redirect('edit_product_variation')
      
  form =   VariationForm(instance=variation)
  context = {
    'form':form,
    'variation':variation,
  }
  return render(request, 'adminapp/editvariation.html', context)

@staff_member_required(login_url= 'admin_login')
def add_product_variation(request):
  
  if request.method == 'POST':
    form = VariationForm(request.POST)
    if form.is_valid():
      form.save()
      messages.success(request, 'Variation added successfully.')
      return redirect('product_variations')
    else:
      messages.error(request, 'Invalid input!!!')
      return redirect('add_product_variation')
    
  form = VariationForm()
  context = {
    'form':form
  }
  return render(request, 'adminapp/addvariation.html', context)


@staff_member_required(login_url = 'admin_login')
def coupons(request):
  coupons = Coupon.objects.all()
  context = {
    'coupons':coupons,
  }
  return render(request, 'adminapp/coupons.html', context)

@staff_member_required(login_url = 'admin_login')
def add_coupon(request):
  if request.method == 'POST':
    form = CouponForm(request.POST , request.FILES)
    if form.is_valid():
      form.save()
      messages.success(request,'Coupon Added successfully')
      return redirect('coupons')
    else:
      messages.error(request, 'Invalid input!!!')
      return redirect('add_coupon')
  form = CouponForm()
  context = {
    'form':form,
  }
  return render(request, 'adminapp/addcoupon.html', context)

@staff_member_required(login_url = 'admin_login')
def edit_coupon(request, id):
  coupon = Coupon.objects.get(id = id)
  if request.method == 'POST':
    form = CouponForm(request.POST , request.FILES, instance=coupon)
    if form.is_valid():
      form.save()
      messages.success(request,'Coupon updated successfully')
      return redirect('coupons')
    else:
      messages.error(request, 'Invalid input!!!')
      return redirect('edit_coupon', coupon.id)
  form = CouponForm(instance=coupon)
  context = {
    'coupon':coupon,
    'form':form,
  }
  return render(request, 'adminapp/editcoupon.html', context)

@staff_member_required(login_url= 'admin_login')
def delete_coupon(request, id):
  coupon = Coupon.objects.get(id = id)
  coupon.delete()
  messages.success(request,'Coupon deleted successfully')
  return redirect('coupons')


#reviews


@staff_member_required(login_url = 'admin_login')
def reviews(request):
  coupons = Coupon.objects.all()
  context = {
    'coupons':coupons,
  }
  return render(request, 'adminapp/coupons.html', context)

@staff_member_required(login_url = 'admin_login')
def add_reviews(request):
  if request.method == 'POST':
    form = CouponForm(request.POST , request.FILES)
    if form.is_valid():
      form.save()
      messages.success(request,'Coupon Added successfully')
      return redirect('coupons')
    else:
      messages.error(request, 'Invalid input!!!')
      return redirect('add_coupon')
  form = CouponForm()
  context = {
    'form':form,
  }
  return render(request, 'adminapp/addcoupon.html', context)


@staff_member_required(login_url= 'admin_login')
def delete_reviews(request, id):
  coupon = Coupon.objects.get(id = id)
  coupon.delete()
  messages.success(request,'Coupon deleted successfully')
  return redirect('coupons')


@staff_member_required(login_url = 'admin_login')
def orders(request):
  orders = Order.objects.filter(is_ordered=True).order_by('-id')
  
  paginator = Paginator(orders, 10)
  page_number = request.GET.get('page')
  page_obj = paginator.get_page(page_number)
  
  context = {
    'orders':page_obj,
  }
  return render(request, 'adminapp/orders.html', context)

@staff_member_required(login_url = 'admin_login')
def update_order(request, id):
  if request.method == 'POST':
    order = get_object_or_404(Order, id=id)
    status = request.POST.get('status')
    order.status = status 
    order.save()
    if status  == "Delivered":
      try:
          payment = Payment.objects.get(payment_id = order.order_number, status = False)
          print(payment)
          if payment.payment_method == 'Cash On Delivery':
              payment.status = True
              payment.save()
      except:
          pass
    order.save()
    
  return redirect('orders')
 

 
@staff_member_required(login_url= 'admin_login')
def sales_report(request):
    year = datetime.now().year
    today = datetime.today()
    month = today.month
    years = []
    today_date=str(date.today())
    start_date=today_date
    end_date=today_date

    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        val = datetime.strptime(end_date, '%Y-%m-%d')
        end_date = val+timedelta(days=1)
        orders = Order.objects.filter(Q(created_at__lte=end_date),Q(created_at__gte=start_date),payment__status = True).values('user_order_page__product__product_name','user_order_page__product__stock',total = Sum('order_total'),).annotate(dcount=Sum('user_order_page__quantity')).order_by('-total')
    else:
        orders = Order.objects.filter(created_at__year = year,created_at__month=month,payment__status = True).values('user_order_page__product__product_name','user_order_page__product__stock',total = Sum('order_total'),).annotate(dcount=Sum('user_order_page__quantity')).order_by('-total')
    
    year = today.year
    for i in range (3):
        val = year-i
        years.append(val)

    context = {
        'orders':orders,
        'today_date':today_date,
        'years':years,
        'start_date':start_date,
        'end_date':end_date,
    }
    return render(request, 'adminapp/sales_report.html', context)

@staff_member_required(login_url= 'admin_login') 
def sales_report_month(request,id):
    orders = Order.objects.filter(created_at__month = id,payment__status = True).values('user_order_page__product__product_name','user_order_page__product__stock',total = Sum('order_total'),).annotate(dcount=Sum('user_order_page__quantity')).order_by()
    today_date=str(date.today())
    context = {
        'orders':orders,
        'today_date':today_date
    }
    return render(request,'adminapp/sales_report_table.html',context)
  
@staff_member_required(login_url='admin_login')
def sales_report_year(request,id):
    orders = Order.objects.filter(created_at__year = id,payment__status = True).values('user_order_page__product__product_name','user_order_page__product__stock',total = Sum('order_total'),).annotate(dcount=Sum('user_order_page__quantity')).order_by()    
    today_date=str(date.today())
    context = {
        'orders':orders,
        'today_date':today_date
    }
    return render(request,'adminapp/sales_report_table.html',context) 

  
def pdf_report(request, start_date, end_date):
    year = datetime.now().year
    today = datetime.today()
    month = today.month
    
    if start_date == end_date:
      orders = Order.objects.filter(created_at__year = year,created_at__month=month,payment__status = True).values('user_order_page__product__product_name','user_order_page__product__stock',total = Sum('order_total'),).annotate(dcount=Sum('user_order_page__quantity')).order_by('-total')
    else:
      orders = Order .objects.filter(Q(created_at__lte=end_date),Q(created_at__gte=start_date),payment__status = True).values('user_order_page__product__product_name','user_order_page__product__stock',total = Sum('order_total'),).annotate(dcount=Sum('user_order_page__quantity')).order_by('-total')
    
    template_path = 'adminapp/sales-report-pdf.html'
    context = {'orders': orders,}
    
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=sales_report' + str(datetime.now()) +'.pdf'
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(
       html, dest=response)
    # if error then show some funny view
    if pisa_status.err:
       return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response
  
  
def excel_report(request, start_date, end_date):
    year = datetime.now().year
    today = datetime.today()
    month = today.month
    
    if start_date == end_date:
      orders = Order.objects.filter(created_at__year = year,created_at__month=month,payment__status = True).values_list('user_order_page__product__product_name', Sum('user_order_page__quantity'),'user_order_page__product__stock', Sum('order_total'))
    else:
      orders = Order.objects.filter(Q(created_at__lte=end_date),Q(created_at__gte=start_date),payment__status = True).values_list('user_order_page__product__product_name', Sum('user_order_page__quantity'),'user_order_page__product__stock', Sum('order_total'))
      
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=sales_report' + str(datetime.now()) +'.xls'
    
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Sales_report')
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True
    
    columns = ['Item Name', 'Item sold', 'In stock', 'Amount Received']
    
    for col_num in range(len(columns)):
      ws.write(row_num, col_num, columns[col_num], font_style)
      
    font_style = xlwt.XFStyle()
    
    rows = orders
    
    for row in rows:
      row_num += 1

      for col_num in range(len(row)):
        ws.write(row_num, col_num, str(row[col_num]), font_style)
        
    wb.save(response)

    return response
    

@staff_member_required(login_url= 'admin_login') 
def category_offers(request):
  categories = Category.objects.all().order_by('-category_offer')
  
  paginator = Paginator(categories, 10)
  page_number = request.GET.get('page')
  page_obj = paginator.get_page(page_number)
  
  context = {
    'categories':page_obj,
  }
  return render(request, 'adminapp/category_offers.html', context)

@staff_member_required(login_url= 'admin_login') 
def add_category_offer(request):
  if request.method == 'POST' :
    category_name = request.POST.get('category_name')
    category_offer = request.POST.get('category_offer')
    category = Category.objects.get(category_name = category_name)
    category.category_offer =  category_offer
    category.save()
    messages.success(request,'Category offer added successfully')
    return redirect('category_offers')
      
@staff_member_required(login_url= 'admin_login') 
def delete_category_offer(request, id):
  category = Category.objects.get(id = id)
  category.category_offer =  0
  category.save()
  messages.success(request,'Category offer deleted successfully')
  return redirect('category_offers')


@staff_member_required(login_url= 'admin_login')  
def product_offers(request):
  products = Product.objects.all().order_by('-product_offer')
  
  paginator = Paginator(products, 10)
  page_number = request.GET.get('page')
  page_obj = paginator.get_page(page_number)
  
  context = {
    'products':page_obj,
  }
  return render(request, 'adminapp/product_offers.html', context)

@staff_member_required(login_url= 'admin_login') 
def add_product_offer(request):
  if request.method == 'POST' :
    product_name = request.POST.get('product_name')
    product_offer = request.POST.get('product_offer')
    product = Product.objects.get(product_name = product_name)
    product.product_offer =  product_offer
    product.save()
    messages.success(request,'Product offer added successfully')
    return redirect('product_offers')
  
@staff_member_required(login_url= 'admin_login') 
def delete_product_offer(request, id):
  product = Product.objects.get(id=id)
  product.product_offer = 0
  product.save()
  messages.success(request, 'Product offer deleted successfully')
  return redirect('product_offers')


#banner

@staff_member_required(login_url='admin_login') 
def banner(request):
    try:
        bannr = Banner.objects.all()
        return render(request, 'adminapp/banner.html', {'bannr': bannr})
    except Exception as e:
        # Log the error or handle it appropriately
        print(f"Error in banner view: {e}")
        return HttpResponse(status=500)  # Internal Server Error

@staff_member_required(login_url='admin_login') 
def add_banner(request):
    try:
        if request.method == "POST":
            banr = Banner()
            if 'image' in request.FILES:
                print('IMAGE UPLOADED')
                banr.banner_image = request.FILES['image']
                banr.save()
                return redirect('banner')
    except Exception as e:
        # Log the error or handle it appropriately
        print(f"Error in add_banner view: {e}")
        return HttpResponse(status=500)  # Internal Server Error
    
    return render(request, 'adminapp/addbanner.html')

@staff_member_required(login_url='admin_login') 
def select_banner(request, id):
    try:
        bannr = Banner.objects.all()
        bannr.update(is_selected=False)
        banners = Banner.objects.filter(id=id)
        banners.update(is_selected=True)
        return redirect('banner')
    except Exception as e:
        # Log the error or handle it appropriately
        print(f"Error in select_banner view: {e}")
        return HttpResponse(status=500)  # Internal Server Error

@staff_member_required(login_url='admin_login') 
def deselect_banner(request, id):
    try:
        bannr = Banner.objects.all()
        bannr.update(is_selected=True)
        banners = Banner.objects.filter(id=id)
        banners.update(is_selected=False)
        return redirect('banner')
    except Exception as e:
        # Log the error or handle it appropriately
        print(f"Error in deselect_banner view: {e}")
        return HttpResponse(status=500)  # Internal Server Error

@staff_member_required(login_url='admin_login') 
def remove_banner(request, id):
    try:
        bannr = Banner.objects.filter(id=id)
        bannr.delete()
        return redirect('banner')
    except Exception as e:
        # Log the error or handle it appropriately
        print(f"Error in remove_banner view: {e}")
        return HttpResponse(status=500)  # Internal Server Error