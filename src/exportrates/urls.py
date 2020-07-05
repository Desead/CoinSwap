from django.urls import path
from src.exportrates.views import xmlrts

urlpatterns = [
    path('', xmlrts),
]
