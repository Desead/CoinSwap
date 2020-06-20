from django.http import JsonResponse
from src.change.models import ChangeModel
from src.core.models import MoneyTypeModel, PaySystemModel
from src.parsers.models import AllRates


#todo есть ли смысл тодступ к /api/ сделать по паролю?
def JsonView(request):
    """
    получаем все обмены, а не через фильтр т.к. тогда можно недоступные обмены сделать неактивными
    также используем промежуточный словарь для того чтобы далее все обмены внести в список. так проще сразу видеть
    сколько всего есть обменов. Самый первый элемент в списке это левая платёжка, остальные - правая
    Также, благодаря использованию промежуточного словаря, левые платёжки сразу делаются уникальными
    на сайте отображаются вообще все омбены которые есть в таблице обменов. Те которые не разрешены менять, на фронте
    просто заблочены, но всё равно там присутствуют
    """
    # todo осталось добавить выбор сайта. пока все настройки не имеют деления по сайтам
    temp2 = list(ChangeModel.objects.all())
    change = ChangeModel.objects.all()
    rates = AllRates.objects.all()
    # freeze = MoneyTypeModel.objects.all()

    # промежуточный словарь temp3, нужен чтобы потом из него легко было сделать список где все обмены собраны в
    # группу по левой платёжке. Используется именно список потому что сразу видно кол-во обменов. Первый элемент в
    # списке это платёжка слева, остальные справа.
    temp3 = {}

    # финальный словарь и используемые в нём ключи
    b = {  # 'changeside': [],
        'img': {}, 'pstype': {}, 'screen_code': {}, 'code_screen': {}, 'time_freeze': {},
        'swap': {}, 'swap_options': {}, 'sort_from': {}, 'sort_to': {}, 'ps_fee_to': {}}

    # составили направления обменов. откуда и куда. Используем множество чтобы удалить повторы
    for i in change:
        b['swap'].setdefault(i.pay_from.code, set())
        b['swap'][i.pay_from.code].add(i.pay_to.code)
    # конвертим множество в список т.к. json не знает что такое множество
    for k, v in b['swap'].items():
        b['swap'][k] = list(b['swap'][k])

    # отдаём разлчные свойства обмена
    for i in change:
        name_swap = i.pay_from.code + '_' + i.pay_to.code
        b['swap_options'].setdefault(name_swap, [])  # список словарей потому что возможны ступенчатые курсы обмена
        b['swap_options'][name_swap].append({})
        count_swap = len(b['swap_options'][name_swap]) - 1
        # todo если резер стал больше баланса то надо запретить приём на эту платёжку
        b['swap_options'][name_swap][count_swap]['active'] = i.active and i.pay_from.active and i.pay_to.active
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
        # test = просто номер, передаётся чтобы легко было определить по какому именно курсу идёт обмен. Надо для ступенчатых обменов, чтобы не путаться в них.
        # Так как там могут быть и ручные и автоматические и т.д.
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

    # for i in temp2:
    #     flag = True  # флаг обмена. обмен действующий или нет
    #     if i.pay_from.code not in temp3:  # сначала создаём словарь со списком
    #         temp3[i.pay_from.code] = [i.pay_from.code]
    #     if i.active and i.pay_from.active and i.pay_to.active:  # добавили активное направление обмена или нет
    #         temp3[i.pay_from.code].append([i.pay_to.code, True])
    #     else:
    #         temp3[i.pay_from.code].append([i.pay_to.code, False])
    #         flag = False
    #
    #     # так как обмены это список списков, то узнаём порядковый номер куда добавлять очередные свойства
    #     num = len(temp3[i.pay_from.code]) - 1
    #     temp3[i.pay_from.code][num].append(i.manual)  # добавили тип обмена, ручной или нет
    #
    #     # todo добавить проверку на наличие курса. Если курса обмена нет, то и выводить эти направления не нужно
    #     #  в иделае сделать эту проверку лучше на моменте формирования курса, чтобы максимально облегчить все расчёты
    #     #  в этом месте
    #
    #     # # путь к логотипам
    #     # if str(i.pay_from.url) != '':
    #     #     b['img'][i.pay_from.code] = str(i.pay_from.url)
    #     # if str(i.pay_to.url) != '':
    #     #     b['img'][i.pay_to.code] = str(i.pay_to.url)
    #
    #     # # передаём связь кода валют с отображением на сайте. Нужно только чтобы делать урлы и понимать какие
    #     # # платёжки сейчас задействованы
    #     # b['screen_code'][i.pay_from.screen] = i.pay_from.code
    #     # b['screen_code'][i.pay_to.screen] = i.pay_to.code
    #     # b['code_screen'][i.pay_from.code] = i.pay_from.screen
    #     # b['code_screen'][i.pay_to.code] = i.pay_to.screen
    #     #
    #     # # тип платёжки: карта, крипта, остальное
    #     # b['pstype'][str(i.pay_from.code)] = i.pay_from.moneytype.moneytype
    #     # b['pstype'][str(i.pay_to.code)] = i.pay_to.moneytype.moneytype
    #
    #     if not flag:  # расчёт курсов обмена дорогая операция, поэтмоу убираем её там где она не нужна
    #         continue
    #
    #     # сделали обмен недоступным так как нету резервов или макс меньге минимума
    #     if (i.pay_from_min > i.pay_from_max) or (i.pay_to_min > min(i.pay_to_max, i.pay_to.reserve)):
    #         temp3[i.pay_from.code][num][1] = False
    #         continue
    #
    #     # todo повесить на фронте клик на минмакс для внесения их в поле обмена
    #     b['stat'][i.pay_from.code + i.pay_to.code + 'minfrom'] = i.pay_from_min
    #     b['stat'][i.pay_from.code + i.pay_to.code + 'maxfrom'] = i.pay_from_max
    #     b['stat'][i.pay_from.code + i.pay_to.code + 'minto'] = i.pay_to_min
    #     b['stat'][i.pay_from.code + i.pay_to.code + 'maxto'] = min(i.pay_to_max, i.pay_to.reserve)
    #     b['stat'][i.pay_from.code + i.pay_to.code + 'reservto'] = i.pay_to.reserve
    #
    #     # b['timefreeze'][i.pay_from.moneytype.moneytype] = i.pay_from.moneytype.freeze
    #     # b['timefreeze'][i.pay_to.moneytype.moneytype] = i.pay_to.moneytype.freeze
    #
    #     # получаем курс обмена
    #     base_money = i.pay_from.usedmoney.usedmoney
    #     profit_money = i.pay_to.usedmoney.usedmoney
    #     if base_money == profit_money:
    #         b['stat'][i.pay_from.code + i.pay_to.code + 'ratefrom'] = 1
    #         rate_final = 1
    #     else:
    #         rate_money = AllRates.objects.get(base=base_money, profit=profit_money)
    #         b['stat'][i.pay_from.code + i.pay_to.code + 'ratefrom'] = rate_money.nominal_1
    #         rate_final = rate_money.nominal_2
    #
    #     # todo сейчас комиссии просто складываюстя и всё, но надо добавить ограничения по комиссиям,
    #     #  к примеру более 1000р не снимается, также добавить фиксированную комиссию, которую может снимать платёжка
    #     # Собираем все комиссии, объязательные платежи и выдаём итоговый курс
    #     fee_pay_system = i.pay_to.fee  # комиссия платёжной системы за перевод
    #     fee_change = i.fee  # комиссия обменника
    #     fee_all = fee_pay_system + fee_change
    #     rate_final = rate_final * ((100 - fee_all) / 100)
    #
    #     b['stat'][i.pay_from.code + i.pay_to.code + 'rate   to'] = rate_final

    # for i in temp3.values():
    #     b['changeside'].append(i)
    # b = {'a': {'as': {'fg': {'hgh': 'fgh','fss':'3rere','2wq':'ads22'},'34fw':'wfew','fa3w':'2fwq'}}, 'b': 15, 'c': 4}
    return JsonResponse(b)
