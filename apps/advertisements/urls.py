"""URL routes for advertisements."""

from django.urls import path

from apps.advertisements.views import AdvertisementListView
from apps.common.views import AdvertisementStatisticsView

app_name = 'advertisements'

urlpatterns = [
    path('', AdvertisementListView.as_view(), name='list'),
    path('statistics/', AdvertisementStatisticsView.as_view(), name='statistics'),
]
