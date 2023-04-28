from django.contrib import admin
from .models import Category, Sub_Category

# Register your models here.

class CategoryAdmin(admin.ModelAdmin):
  prepopulated_fields = {'slug': ('category_name',)}
  list_display = ('category_name', 'slug')

admin.site.register(Category, CategoryAdmin)

class Sub_CategoryAdmin(admin.ModelAdmin):
  prepopulated_fields = {'slug':('sub_category_name',)}
  list_display = ('sub_category_name', 'slug', 'is_featured')

admin.site.register(Sub_Category, Sub_CategoryAdmin)