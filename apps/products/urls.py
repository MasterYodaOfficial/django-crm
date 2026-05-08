"""URL routes for products."""

from django.urls import path

from apps.products.views import (
    ProductCreateView,
    ProductDeleteView,
    ProductDetailView,
    ProductListView,
    ProductUpdateView,
)

app_name = 'products'

urlpatterns = [
    path('', ProductListView.as_view(), name='list'),
    path('new/', ProductCreateView.as_view(), name='create'),
    path('<int:pk>/', ProductDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', ProductUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', ProductDeleteView.as_view(), name='delete'),
]
