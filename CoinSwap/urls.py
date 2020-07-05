"""CoinSwap URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from CoinSwap import settings

urlpatterns = [
    path('clear/', include('src.clearingbd.urls')),
    path('core/', include('src.core.urls')),
    path(settings.XML_RATES_SITE1, include('src.exportrates.urls')),
    path('api/', include('src.api.urls')),
    path('admin/', admin.site.urls),
    path('', include('src.frontend.urls')),
]

# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)