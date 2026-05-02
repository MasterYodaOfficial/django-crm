"""URL configuration for django_crm project."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(  # type: ignore[arg-type]
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
