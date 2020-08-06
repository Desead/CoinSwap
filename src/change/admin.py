from django.contrib import admin
from src.change.models import ChangeModel, OrderModel
from src.core.models import PaySystemModel


# admin.site.register(OrderModel)
# admin.site.register(ChangeModel)

@admin.register(OrderModel)
class OrderModelAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Общая информация о заявке',
         {'fields': ['status', 'site', 'url_change', 'num', 'numuuid', 'data_create', 'data_change']}),
        ('Клиент перевёл', {'fields': ['pay_from', 'sum_from', 'sum_from_rub', ]}),
        ('Клиент получил', {'fields': ['pay_to', 'sum_to', 'sum_to_rub', ]}),
        ('Расчёты',
         {'fields': ['rate', 'rate_best', 'rate_cb', 'fee', 'profit', 'profit_rub', 'partner', 'partner_rub', ]}),
        ('Кошельки', {'fields': ['wallet_client_from', 'wallet_client_to', 'wallet_exchange_to', 'wallet_exchange_from',
                                 'wallet_add', ]}),
        ('Остатки', {'fields': ['lock', 'description', ]}),
    ]
    list_display = ('num', 'site', 'status', 'pay_from', 'pay_to', 'sum_from', 'sum_to', 'data_create')
    list_display_links = ('num', 'status',)
    list_filter = ['status', 'site']
    readonly_fields = (
        'site', 'num', 'numuuid', 'data_create', 'data_change', 'pay_from', 'sum_from', 'sum_from_rub', 'pay_to',
        'sum_to', 'sum_to_rub', 'wallet_add',
        'fee', 'rate', 'rate_best', 'rate_cb',
        'profit', 'profit_rub', 'url_change',
        'partner', 'partner_rub',
        'fee_client', 'wallet_client_from', 'wallet_exchange_to', 'wallet_exchange_from', 'wallet_client_to', 'lock',)

    save_on_top = True


@admin.register(ChangeModel)
class ChangeModelAdmin(admin.ModelAdmin):

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'pay_from' or db_field.name == 'pay_to':
            kwargs["queryset"] = PaySystemModel.objects.filter(active=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    list_display = ('pk',
                    'site', 'pay_from', 'pay_from_min', 'pay_from_max', 'pay_to', 'pay_to_min', 'pay_to_max', 'fee',
                    'fee_fix',
                    'active', 'dinamic_fee', 'manual')
    list_editable = (
        'pay_from_min', 'pay_from_max', 'pay_to_min', 'pay_to_max', 'fee', 'active', 'dinamic_fee', 'manual', 'fee_fix')
    list_display_links = ('pay_from', 'pay_to')
    list_filter = ('active', 'dinamic_fee', 'manual', 'site')
    save_as = True
    save_on_top = True

    fieldsets = [
        ('', {'fields': ['site', 'description']}),
        ('Платёжные системы', {'fields': ['pay_from', 'pay_from_min', 'pay_from_max', 'pay_to', 'pay_to_min', 'pay_to_max']}),
        ('Комиссии', {'fields': ['fee', 'fee_fix', 'fee_min', 'fee_max', ]}),
        ('Метки', {
            'fields': ['active', 'dinamic_fee', 'manual', 'juridical', 'verifying', 'cardverify', 'floating', 'otherin', 'otherout', 'reg',
                       'card2card', 'city_change']}),
        ('SEO', {'fields': ['title_text', 'description_text', 'keywords_text']}),
    ]
