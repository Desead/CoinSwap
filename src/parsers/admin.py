from django.contrib import admin

from src.parsers.library import best
from src.parsers.models import CBRF, BSexchange, Binance, AllRates


@admin.register(CBRF)
class FiatRatesCBRFAdmin(admin.ModelAdmin):
    list_display = ('name', 'nominal_1', 'nominal_2', 'base', 'profit', 'source', 'dt')
    list_display_links = ('name', 'base', 'profit')
    list_filter = ('base', 'profit', 'source')


@admin.register(Binance)
class BinanceAdmin(admin.ModelAdmin):
    list_display = ('name', 'nominal_1', 'nominal_2', 'base', 'profit', 'source', 'dt')
    list_display_links = ('name', 'base', 'profit')
    list_filter = ('base', 'profit', 'source')


@admin.register(BSexchange)
class BSexchangeAdmin(admin.ModelAdmin):
    list_display = ('name', 'idexch', 'ignore')
    list_display_links = ('name', 'idexch')
    search_fields = ['name']
    list_filter = ['ignore']
    list_editable = ['ignore']
    actions = ['GetFromBestFile']

    # Получать список обменников наверное раз в неделю можно. нет смысла чаще
    def GetFromBestFile(self, request, queryset):
        best.loadFiles()
        a = best.getData('bm_exch.dat', 1)
        if len(a) > 0:
            BSexchange.objects.all().delete()
            for k, v in a.items():
                temp = BSexchange()
                temp.idexch = k
                temp.name = v
                temp.save()

        self.message_user(request, 'Обменники с bestchange получены')

    GetFromBestFile.short_description = 'Получить обменники с Bestchange'
    GetFromBestFile.allowed_permissions = ('change', 'add', 'delete', 'view')


@admin.register(AllRates)
class AllRatesAdmin(admin.ModelAdmin):
    list_display = ('name', 'base', 'profit', 'nominal_1', 'nominal_2', 'source')
    list_display_links = ('name', 'base', 'profit')
    list_filter = ('source', 'base', 'profit')
