from django.urls import path
from .views import proxy_handler

urlpatterns = [
    path('proxy/', proxy_handler, name='proxy_handler'),
]
