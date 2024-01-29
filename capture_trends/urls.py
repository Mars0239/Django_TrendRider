# capture_trends/urls.py

from django.urls import path
from .views import stock_template_view, stock_data_view

urlpatterns = [
    path('', stock_template_view, name='stock_template_view'),
    path('data/', stock_data_view, name='stock_data_view'),
]
