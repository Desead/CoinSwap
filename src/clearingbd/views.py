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

    # if request.GET.get('settings') == 'rates':
    #     cnt = 0
    #     a = best.getRates()
    #     if len(a) > 0:
    #         BSrates.objects.all().delete()
    #         for i in a:
    #             if len(i) < 6:
    #                 continue
    #             temp = BSrates()
    #             temp.curfrom = i[0]
    #             temp.curto = i[1]
    #             temp.exch = i[2]
    #             temp.ratefrom = i[3]
    #             temp.rateto = i[4]
    #             temp.res = i[5]
    #             temp.dt = datetime.datetime.now()
    #             temp.save()
    #             cnt += 1
    #             if cnt >= 100:
    #                 break

    if request.GET.get('settings') == 'all':
        AllRates.objects.all().delete()
        bn = Binance.objects.all()
        cb = CBRF.objects.all()

    return render(request, 'clearingbd/clear.html')
