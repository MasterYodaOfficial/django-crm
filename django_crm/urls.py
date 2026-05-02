"""URL configuration for django_crm project."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.urls import include, path

from apps.common.views import CRMLoginView

urlpatterns = [
    path('', include('apps.common.urls')),
    path('accounts/login/', CRMLoginView.as_view(), name='login'),
    path('accounts/logout/', LogoutView.as_view(), name='logout'),
    path('products/', include('apps.products.urls')),
    path('ads/', include('apps.advertisements.urls')),
    path('leads/', include('apps.leads.urls')),
    path('customers/', include('apps.customers.urls')),
    path('contracts/', include('apps.contracts.urls')),
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
