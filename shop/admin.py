from django.contrib import admin
from .models import Product, Variation , ProductReview

# Register your models here.

class ProductAdmin(admin.ModelAdmin):
  list_display = ('product_name', 'price', 'stock', 'category', 'sub_category', 'modified_date', 'is_featured', 'is_available')
  prepopulated_fields = {'slug':('product_name',)}

class VariationAdmin(admin.ModelAdmin):
  list_display = ('product','variation_category','variation_value','is_active')
  list_editable = ('is_active',)
  list_filter = ('product','variation_category','variation_value',)

class ProductReviewAdmin(admin.ModelAdmin):
  list_display = ('user', 'product', 'review_text', 'review_rating')
  

  
admin.site.register(Product,ProductAdmin)
admin.site.register(Variation, VariationAdmin)
admin.site.register(ProductReview, ProductReviewAdmin)
