from django.urls import path
from .views import PaySystems, Change, Info, Bestchange, Bin, Cbrf, Order, Begin, Rates, CBRFFormView

urlpatterns = [
    path('', Order.as_view(), name='orders'),
    path('pay/', PaySystems.as_view(), name='paysystem'),
    path('change/', Change.as_view(), name='change'),
    # path('info/', Info.as_view(), name='info'),
    path('info/', CBRFFormView, name='info'),
    path('best/', Bestchange.as_view(), name='best'),
    path('cbrf/', Cbrf.as_view(), name='cbrf'),
    path('rates/', Rates.as_view(), name='rates'),
    path('binance/', Bin.as_view(), name='binance'),
    path('begin/', Begin.as_view(), name='begin'),

]
