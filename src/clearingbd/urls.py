from django.urls import path
from src.clearingbd import views

urlpatterns = [
    path('', views.clearbd),
]
