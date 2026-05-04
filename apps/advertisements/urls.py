"""URL routes for advertisements."""

from django.urls import path

from apps.advertisements.views import (
    AdvertisementCreateView,
    AdvertisementDeleteView,
    AdvertisementDetailView,
    AdvertisementListView,
    AdvertisementUpdateView,
)
from apps.common.views import AdvertisementStatisticsView

app_name = 'advertisements'

urlpatterns = [
    path('', AdvertisementListView.as_view(), name='list'),
    path('new/', AdvertisementCreateView.as_view(), name='create'),
    path('<int:pk>/', AdvertisementDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', AdvertisementUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', AdvertisementDeleteView.as_view(), name='delete'),
    path('statistics/', AdvertisementStatisticsView.as_view(), name='statistics'),
]
