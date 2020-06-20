from django.urls import path
from src.api import views

urlpatterns = [
    path('', views.JsonView)
]
