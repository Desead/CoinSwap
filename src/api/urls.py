from django.urls import path
from src.api.views import JsonView

urlpatterns = [
    path('', JsonView)
]
