from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.views.static import serve
from django.contrib import admin

urlpatterns = [
        path("admin/", admin.site.urls),

    path('', include('shop.urls')),
    path('adminn/', include('adminapp.urls')),
    path('accounts/', include('account.urls')),
    path('cart/', include('carts.urls')),
    path('orders/', include('orders.urls')),
    path('wishlist/', include('wishlist.urls')),
]

if settings.DEBUG:
    urlpatterns += [
        path('media/<path:path>', serve, {'document_root': settings.MEDIA_ROOT}),
        path('static/<path:path>', serve, {'document_root': settings.STATIC_ROOT}),
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
