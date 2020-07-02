from django.http import JsonResponse
from src.change.models import ChangeModel
from src.parsers.models import AllRates


# todo есть ли смысл доступ к /api/ сделать по паролю?
def JsonView(request):
    """
    получаем все обмены, а не через фильтр т.к. тогда можно недоступные обмены сделать неактивными
    также используем промежуточный словарь для того чтобы далее все обмены внести в список. так проще сразу видеть
    сколько всего есть обменов. Самый первый элемент в списке это левая платёжка, остальные - правая
    Также, благодаря использованию промежуточного словаря, левые платёжки сразу делаются уникальными
    на сайте отображаются вообще все омбены которые есть в таблице обменов. Те которые не разрешены менять, на фронте
    просто заблочены, но всё равно там присутствуют
    """

    change = ChangeModel.objects.filter(site__url__icontains=request.headers['Host'])
    rates = AllRates.objects.all()

    # финальный словарь и используемые в нём ключи
    b = {'img': {}, 'pstype': {}, 'screen_code': {}, 'code_screen': {}, 'time_freeze': {},
         'swap': {}, 'swap_options': {}, 'sort_from': {}, 'sort_to': {}, 'ps_fee_to': {}}

    # составили направления обменов. откуда и куда. Используем множество чтобы удалить повторы
    for i in change:
        b['swap'].setdefault(i.pay_from.code, set())
        b['swap'][i.pay_from.code].add(i.pay_to.code)
    # конвертим множество в список т.к. json не знает что такое множество
    for k, v in b['swap'].items():
        b['swap'][k] = list(b['swap'][k])

    # отдаём различные свойства обмена
    for i in change:
        name_swap = i.pay_from.code + '_' + i.pay_to.code
        b['swap_options'].setdefault(name_swap, [])  # список словарей потому что возможны ступенчатые курсы обмена
        b['swap_options'][name_swap].append({})
        count_swap = len(b['swap_options'][name_swap]) - 1
        b['swap_options'][name_swap][count_swap][
            'active'] = i.active and i.pay_from.active and i.pay_to.active_out and i.pay_to.active and (
                i.pay_from.reserve < i.pay_from.max_balance)
        b['swap_options'][name_swap][count_swap]['manual'] = i.manual
        b['swap_options'][name_swap][count_swap]['juridical'] = i.juridical
        b['swap_options'][name_swap][count_swap]['verifying'] = i.verifying
        b['swap_options'][name_swap][count_swap]['cardverify'] = i.cardverify
        b['swap_options'][name_swap][count_swap]['floating'] = i.floating
        b['swap_options'][name_swap][count_swap]['otherin'] = i.otherin
        b['swap_options'][name_swap][count_swap]['otherout'] = i.otherout
        b['swap_options'][name_swap][count_swap]['reg'] = i.reg
        b['swap_options'][name_swap][count_swap]['card2card'] = i.card2card
        b['swap_options'][name_swap][count_swap]['pay_from_min'] = i.pay_from_min
        b['swap_options'][name_swap][count_swap]['pay_from_max'] = i.pay_from_max
        b['swap_options'][name_swap][count_swap]['pay_to_min'] = i.pay_to_min
        b['swap_options'][name_swap][count_swap]['pay_to_max'] = min(i.pay_to_max, i.pay_to.reserve)
        b['swap_options'][name_swap][count_swap]['fee'] = i.fee
        b['swap_options'][name_swap][count_swap]['fee_fix'] = i.fee_fix
        b['swap_options'][name_swap][count_swap]['test_num'] = i.pk

        # получаем курс обмена
        base_money = i.pay_from.usedmoney.usedmoney
        profit_money = i.pay_to.usedmoney.usedmoney
        if base_money == profit_money:
            b['swap_options'][name_swap][count_swap]['rate_from'] = 1
            b['swap_options'][name_swap][count_swap]['rate_to'] = 1
        else:
            b['swap_options'][name_swap][count_swap]['rate_from'] = rates.get(base=base_money,
                                                                              profit=profit_money).nominal_1
            b['swap_options'][name_swap][count_swap]['rate_to'] = rates.get(base=base_money,
                                                                            profit=profit_money).nominal_2

    for i in change:
        # отдаём место платёжки. для сортировки
        b['sort_from'][i.pay_from.code] = i.pay_from.sort_from
        b['sort_to'][i.pay_to.code] = i.pay_to.sort_to

        # отдаём комиссии платёжной системы
        b['ps_fee_to'][i.pay_to.code] = {}
        b['ps_fee_to'][i.pay_to.code]['fee'] = i.pay_to.fee
        b['ps_fee_to'][i.pay_to.code]['fee_fix'] = i.pay_to.fee_fix
        b['ps_fee_to'][i.pay_to.code]['fee_min'] = i.pay_to.fee_min
        b['ps_fee_to'][i.pay_to.code]['fee_max'] = min(i.pay_to.fee_max, i.pay_to.reserve_for_site)
        b['ps_fee_to'][i.pay_to.code]['reserve'] = i.pay_to.reserve_for_site

        # передаём связь кода валют с отображением на сайте.
        b['screen_code'][i.pay_from.screen] = i.pay_from.code
        b['screen_code'][i.pay_to.screen] = i.pay_to.code
        b['code_screen'][i.pay_from.code] = i.pay_from.screen
        b['code_screen'][i.pay_to.code] = i.pay_to.screen

        # тип платёжки: карта, крипта, остальное
        b['pstype'][str(i.pay_from.code)] = i.pay_from.moneytype.moneytype
        b['pstype'][str(i.pay_to.code)] = i.pay_to.moneytype.moneytype

        # время заморозки курса при ожидании перевода от клиента
        b['time_freeze'][i.pay_from.moneytype.moneytype] = i.pay_from.moneytype.freeze
        b['time_freeze'][i.pay_to.moneytype.moneytype] = i.pay_to.moneytype.freeze

        # путь к логотипам
        if str(i.pay_from.url) != '':
            b['img'][i.pay_from.code] = str(i.pay_from.url)
        if str(i.pay_to.url) != '':
            b['img'][i.pay_to.code] = str(i.pay_to.url)

    return JsonResponse(b)
