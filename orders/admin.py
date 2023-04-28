from django.contrib import admin
from .models import *

# Register your models here.

class OrderProductInline(admin.TabularInline):
  model = OrderProduct
  extra = 0

class OrderAdmin(admin.ModelAdmin):
  list_display = ['order_number', 'full_name', 'phone', 'email', 'order_total', 'status', 'is_ordered']
  list_per_page =  20
  inlines = [OrderProductInline]

admin.site.register(Payment,)
admin.site.register(Order,OrderAdmin)
admin.site.register(OrderProduct,)
admin.site.register(Address,)
admin.site.register(Coupon)
admin.site.register(UserCoupon)