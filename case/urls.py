from django.conf import settings
from django.conf.urls.static import static
from django.urls import path,include


urlpatterns = [
    path('',include('shop.urls')),
    path('adminn/',include('adminapp.urls')),
    path('accounts/',include('account.urls')),
    path('cart/', include('carts.urls')),
    path('orders/', include('orders.urls')),
    path('wishlist/', include('wishlist.urls')),
    

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
