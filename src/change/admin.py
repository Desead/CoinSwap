from django.contrib import admin
from src.change.models import ChangeModel, OrderModel
from src.core.models import PaySystemModel


# admin.site.register(OrderModel)
# admin.site.register(ChangeModel)

@admin.register(OrderModel)
class OrderModelAdmin(admin.ModelAdmin):
    list_display = ('num', 'status', 'pay_from', 'pay_to', 'sum_from', 'sum_to', 'data_create')
    list_filter = ['status']
    # readonly_fields = (
    # 'site', 'num', 'numuuid', 'data_create', 'data_change', 'pay_from', 'pay_to', 'sum_from', 'sum_to', 'wallet_add',)


@admin.register(ChangeModel)
class ChangeModelAdmin(admin.ModelAdmin):

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'pay_from' or db_field.name == 'pay_to':
            kwargs["queryset"] = PaySystemModel.objects.filter(active=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    list_display = ('pk',
        'site', 'pay_from', 'pay_from_min', 'pay_from_max', 'pay_to', 'pay_to_min', 'pay_to_max', 'fee', 'fee_fix',
        'active', 'dinamic_fee', 'manual')
    list_editable = (
        'pay_from_min', 'pay_from_max', 'pay_to_min', 'pay_to_max', 'fee', 'active', 'dinamic_fee', 'manual','fee_fix')
    list_display_links = ('pay_from', 'pay_to')
    list_filter = ('active', 'dinamic_fee', 'manual', 'site')
    save_as = True
    save_on_top = True
