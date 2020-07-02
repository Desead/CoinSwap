from django.shortcuts import render
from django.utils.datetime_safe import datetime

from src.parsers.library import best
from src.parsers.models import BSexchange, Binance, CBRF, AllRates


def clearbd(request):
    if request.GET.get('settings') == 'info':
        best.loadFiles()

    if request.GET.get('settings') == 'exchange':
        # Получать список обменников наверное раз в неделю можно. нет смысла чаще
        a = best.getData('bm_exch.dat', 1)
        if len(a) > 0:
            BSexchange.objects.all().delete()
            for k, v in a.items():
                temp = BSexchange()
                temp.idexch = k
                temp.name = v
                temp.save()

    if request.GET.get('settings') == 'all':
        AllRates.objects.all().delete()
        bn = Binance.objects.all()
        cb = CBRF.objects.all()

    return render(request, 'clearingbd/clear.html')
