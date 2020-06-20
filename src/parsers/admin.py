from django.contrib import admin
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


@admin.register(AllRates)
class AllRatesAdmin(admin.ModelAdmin):
    list_display = ('name', 'base', 'profit', 'nominal_1', 'nominal_2', 'source')
    list_display_links = ('name', 'base', 'profit')
    list_filter = ('source', 'base', 'profit')
