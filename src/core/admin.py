from django.contrib import admin

from src.core.models import PaySystemModel, UsedMoneyModel, SiteModel, MoneyTypeModel, CityModel, \
    WalletsModel

admin.site.register(UsedMoneyModel)
admin.site.register(CityModel)


@admin.register(WalletsModel)
class WalletsModelAdmin(admin.ModelAdmin):

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'pay':
            kwargs["queryset"] = PaySystemModel.objects.filter(active=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    list_display = ('pay', 'name', 'count_in', 'count_out', 'max_trans', 'max_balance', 'date')
    save_as = True


@admin.register(MoneyTypeModel)
class MoneyTypeModelAdmin(admin.ModelAdmin):
    list_display = ('moneytype', 'description', 'freeze', 'freeze_confirm')
    list_editable = ('freeze', 'freeze_confirm')
    list_display_links = ('moneytype',)
    list_filter = ['freeze']


@admin.register(PaySystemModel)
class PaySystemsAdmin(admin.ModelAdmin):
    list_display = (
        'screen', 'code', 'idbest', 'active', 'moneytype', 'usedmoney', 'max_balance', 'reserve', 'reserve_for_site',
        'fee', 'fee_fix',
        'fee_min', 'fee_max', 'url')
    list_display_links = ('screen', 'code', 'moneytype', 'usedmoney', 'idbest')
    list_filter = ('active', 'moneytype', 'usedmoney')
    list_editable = ('active', 'max_balance', 'reserve', 'fee', 'fee_fix', 'fee_min', 'fee_max', 'reserve_for_site')
    search_fields = ('code', 'screen')
    save_on_top = True


@admin.register(SiteModel)
class SitesAdmin(admin.ModelAdmin):
    list_display = ('name', 'url',)
