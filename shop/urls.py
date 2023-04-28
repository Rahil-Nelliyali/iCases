from django.urls import path
from . import views

urlpatterns = [
  path('', views.home, name='home'),
  path('change_password/', views.change_password, name='change_password'),
  path('forgot_password/', views.forgot_password, name='forgot_password'),
  path('verify-email/', views.verify_email, name='verify-email'),
  path('reset_password', views.reset_password, name='reset_password'),
  path('resend_otp', views.resend_otp, name='resend-otp'),


  path('shop/', views.shop, name='shop'),
  path('shop/<slug:category_slug>/', views.shop, name='products_by_category'),
  path('shop/<slug:category_slug>/<slug:sub_category_slug>/', views.shop, name='products_by_sub_category'),
  path('shop_filter/', views.shop, name='shop_filter'),
  
  path('shop/<slug:category_slug>/<slug:sub_category_slug>/<slug:product_slug>/', views.product_details, name='product_details'),
  
  path('price_change/', views.price_change, name='price_change'),
  
  path('search/', views.search, name='search'),
  path('get_product_names/', views.get_product_names, name='get_product_names'),
  path('sub_category/', views.sub_category, name='sub_category'),
  
  path('contact/', views.contact, name='contact'),
  path('save-review/<int:product_id>', views.save_review, name='save_review'),
  


   

]