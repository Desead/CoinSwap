from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.timezone import now
from django.views.generic.base import View
from src.change.models import OrderModel, ChangeModel
from src.core.models import PaySystemModel, SiteModel, RegisteredUserModel
from src.frontend.library import addfunc
from src.parsers.models import AllRates


class StartView(View):

    def get(self, request):

        queryset_site = SiteModel.objects.filter(url__icontains=request.headers['Host'])
        if queryset_site.count() != 1:
            return HttpResponse('Сайт не найден')

        queryset_order = OrderModel.objects.filter(site__url__icontains=request.headers['Host'], status='ok')

        queryset_site = queryset_site[0]
        context = {}

        if queryset_site.technical_work:
            context['text'] = queryset_site.technical_text
            return render(request, 'pause.html', context)

        context['description'] = queryset_site.description_text
        context['keywords'] = queryset_site.keywords_text
        context['title'] = queryset_site.title_text
        context['banner'] = queryset_site.banner
        context['news'] = queryset_site.news
        context['order'] = '' if queryset_order.count() <= 0 else queryset_order[0].num

        return render(request, 'index.html', context)


class RulesView(View):
    def get(self, request):
        context = {'host_name': request.headers['Host'].split(':')[0]}
        return render(request, 'rules.html', context)


class ContactView(View):
    def get(self, request):
        temp = SiteModel.objects.filter(url__icontains=request.headers['Host'])
        context = {}
        if temp.count() == 1:
            context = {'mail': temp[0].mail,
                       'time': temp[0].working}
        return render(request, 'contacts.html', context)


class ConfirmView(View):
    """ Коды ошибок
    100 - Не найден обмен с указанными платёжками
    101 - Сюда не должны попасть вообще
    102 - Указанный статус заявки отсутствует
    103 - нет параметра test_num. значит не вызывалась js функция rates.
    104 - test_num не число
    105,106 - полученный код платёжки не найден
    1050,1060 - Платёжки не активны
    1061 - С платёжки нельзя отдавать
    107 - uuid странный
    108,109 - отдаваемая, получаемая сумма <= 0
    110 -
    111 - неверный номер телефона
    112 - номер обмена передали неверно
    113 - неверная почта
    115,114 - клиентом указаны неверные кошельки
    116 - что то не так с дополнительным полем для крипты
    117 - проблемы с доп. полем для крипты
    1171 - доп поле для крипты слишком длинное
    118 - не попали в мин\макс
    """

    context = {}

    # todo если в action вставили другие платёжки, которые тоже есть? или изменил название кнопок

    # берём данные заявки из бд и заполняем их в словарь для вывода
    def get_order_for_bd(self, request, left, right, idfromsite):

        order_model = OrderModel.objects.filter(numuuid=idfromsite, pay_from__code=left, pay_to__code=right)
        if order_model.count() != 1:
            return False,
        order_model = order_model[0]

        # Узнаём название статуса заявки
        order_status = ''
        for i in order_model.STATUS_CHOISES:
            if i[0] == order_model.status:
                order_status = i[1]
                break

        self.context = {'left': order_model.pay_from.screen,
                        'right': order_model.pay_to.screen,
                        'sum_from': order_model.sum_from,
                        'sum_to': order_model.sum_to,
                        'wallet_client_to': order_model.wallet_client_to,
                        'wallet_client_from': order_model.wallet_client_from,
                        'num': order_model.num,
                        'date_create': order_model.data_create.strftime('%Y/%m/%d %H:%M:%S'),
                        'type': order_model.pay_from.moneytype.moneytype,
                        'type_freeze': order_model.pay_from.moneytype.freeze,
                        'type_freeze_confirm': order_model.pay_from.moneytype.freeze_confirm,
                        'text': order_model.text,
                        'status': order_status,
                        }
        return True, order_model.status, order_model.num, order_model.pay_from.moneytype.moneytype

    def check_adress_data(self, request, left, right, idfromsite, queryset):
        # проверили наличие плаёжки и разршение их использования
        temp = queryset.filter(code=left)
        if temp.count() != 1:
            return False, '105'
        temp = temp[0]
        if not temp.active:
            return False, '1050'

        temp = queryset.filter(code=right)
        if temp.count() != 1:
            return False, '106'
        temp = temp[0]
        if not temp.active:
            return False, '1060'
        if not temp.active_out:
            return False, '1061'

        if addfunc.check_uuid(idfromsite) == '':
            return False, '107'

        return True,

    def check_post_data(self, request, right):
        post_data = {}
        post_data['sum_from'] = addfunc.str2float(request.POST.get('sum_from', '0'))
        post_data['sum_to'] = addfunc.str2float(request.POST.get('sum_to', '0'))
        post_data['sumlock'] = 'sumtolock' if request.POST.get('sumlock') == 'sumtolock' else 'sumfromlock'
        post_data['fee_client'] = max(addfunc.str2float(request.POST.get('fee_client', '0')), 0)
        post_data['nmphone'] = addfunc.test_phone(request.POST.get('nmphone', '0'))
        post_data['test_num'] = addfunc.str2int(request.POST.get('test_num', '0'))
        post_data['nmmail'] = addfunc.check_mail(request.POST.get('nmmail', ''))
        # todo как проверить кошельки И дополнительное поле для крипты?
        post_data['wallet_client_from'] = request.POST.get('wallet_client_from', False)
        post_data['wallet_client_to'] = request.POST.get('wallet_client_to', False)
        post_data['wallet_add'] = request.POST.get('wallet_add', False)

        if (right == 'EOS') or (right == 'XRP'):
            if post_data['wallet_add'] == '':
                return False, '117'
            if len(post_data['wallet_add']) > 50:
                return False, '1171'

        if post_data['sum_from'] <= 0:
            return False, '108'
        if post_data['sum_to'] <= 0:
            return False, '109'
        if post_data['nmphone'] <= 0:
            return False, '111'
        if post_data['test_num'] <= 0:
            return False, '112'
        if post_data['nmmail'] == '':
            return False, '113'
        if post_data['wallet_client_from']:
            if addfunc.check_wallet(post_data['wallet_client_from']) == '':
                return False, '114'
        if post_data['wallet_client_to']:
            if addfunc.check_wallet(post_data['wallet_client_to']) == '':
                return False, '115'
        if post_data['wallet_add']:
            if addfunc.check_wallet_add(post_data['wallet_add']) == '':
                return False, '116'

        return True, post_data

    def get(self, request, left, right, idfromsite):
        temp = self.get_order_for_bd(request, left, right, idfromsite)
        if temp[0]:
            if temp[1] == 'cancel':
                return render(request, 'cancel.html', {'order_num': temp[2]})
            else:
                if temp[3] == 'crypto':
                    return render(request, 'confirm_crypto.html', self.context)
            return render(request, 'confirm.html', self.context)
        else:
            return render(request, 'order_not_found.html')

    def post(self, request, left, right, idfromsite):

        # проверяем данные переданные в адресной строке
        temp = self.check_adress_data(request, left, right, idfromsite, PaySystemModel.objects.all())
        if temp[0] == False:
            return render(request, 'error.html', {'error': 'Что то пошло не так. Код ошибки: ' + temp[1]})

        if request.POST.get('checkinput', '0') == 'Далее':
            # проверяем данные из пост запроса
            temp = self.check_post_data(request, right)
            if temp[0] == False:
                return render(request, 'error.html', {'error': 'Что то пошло не так. Код ошибки: ' + temp[1]})
            post_data = temp[1]

            change = ChangeModel.objects.filter(active=True, pay_from__code=left, pay_to__code=right,
                                                pk=post_data['test_num'])

            if change.count() != 1:
                return render(request, 'error.html', {'error': 'Что то пошло не так. Код ошибки: 100'})
            text = ''
            change = change[0]
            if change.manual:
                text = change.text

            # проверем корректность сумм для обмена Всё пересчитываем

            rates = AllRates.objects.all()

            if post_data['sumlock'] == 'sumtolock':
                temp = (post_data['sum_to'] + change.fee_fix + post_data['fee_client']) * 100 / (100 - change.fee)
                temp = round(temp - post_data['sum_to'], 8 if change.pay_to.moneytype.moneytype == 'crypto' else 2)
                temp = max(temp, change.fee_min)
                temp = temp + post_data['sum_to']
                post_data['sum_from'] = round(temp * rates.get(base=change.pay_from.usedmoney.usedmoney,
                                                               profit=change.pay_to.usedmoney.usedmoney).nominal_1 / rates.get(
                    base=change.pay_from.usedmoney.usedmoney, profit=change.pay_to.usedmoney.usedmoney).nominal_2,
                                              8 if change.pay_from.moneytype.moneytype == 'crypto' else 2)
            else:
                # посчитали сумму которую нужно отдать просто по курсу обмена
                out_money = round(post_data['sum_from'] * rates.get(base=change.pay_from.usedmoney.usedmoney,
                                                                    profit=change.pay_to.usedmoney.usedmoney).nominal_2 / rates.get(
                    base=change.pay_from.usedmoney.usedmoney, profit=change.pay_to.usedmoney.usedmoney).nominal_1,
                                  8 if change.pay_to.moneytype.moneytype == 'crypto' else 2)

                # отдельно считаем комиссию за обмен
                fee = out_money * change.fee / 100 + change.fee_fix
                if change.fee_min > 0:
                    fee = max(fee, change.fee_min)
                if change.fee_max > 0:
                    fee = min(fee, change.fee_max)
                fee = round(fee, 8 if change.pay_to.moneytype.moneytype == 'crypto' else 2)

                post_data['sum_to'] = round(max(out_money - fee - post_data['fee_client'], 0),
                                            8 if change.pay_to.moneytype.moneytype == 'crypto' else 2)

            # проверяем полученные суммы обмена на попадание в границы мин и макс
            if (post_data['sum_from'] < change.pay_from_min) or (post_data['sum_from'] > change.pay_from_max) or (
                    post_data['sum_to'] < change.pay_to_min) or (
                    post_data['sum_to'] > change.pay_to_max):
                return render(request, 'error.html', {'error': 'Что то пошло не так. Код ошибки: 118'})

            order_model = OrderModel.objects.filter(numuuid=idfromsite, pay_from__code=left, pay_to__code=right)
            if not order_model.exists():  # если такой записи нет то создаём её
                order = OrderModel()
                order.sum_from = post_data['sum_from']
                order.sum_to = post_data['sum_to']
                order.wallet_client_from = post_data['wallet_client_from']
                order.wallet_client_to = post_data['wallet_client_to']
                order.wallet_exchange_to = ''
                order.wallet_exchange_from = ''
                order.wallet_add = post_data['wallet_add']
                order.fee_client = post_data['fee_client']
                order.lock = 'sumtolock' if post_data['sumlock'] == 'sumtolock' else 'sumfromlock'
                order.pay_from = PaySystemModel.objects.get(code=left)
                order.pay_to = PaySystemModel.objects.get(code=right)
                # todo не работает выбор пользователя и сайта
                # x = RegisteredUserModel.objects.filter(user_site__url__icontains=request.headers['Host'])
                # x1 = RegisteredUserModel.objects.filter(user_site__url__icontains=request.headers['Host'])[0]
                # order.client = RegisteredUserModel.objects.filter(user_site__url__icontains=request.headers['Host'])[0]
                order.num = 100 + OrderModel.objects.all().count()
                order.site = SiteModel.objects.filter(url__icontains=request.headers['Host'])[0]
                order.data_create = order.data_change = now()
                order.numuuid = idfromsite
                order.text = text
                order.url_change = request.headers['Origin'] + '/' + left + '/' + right + '/' + idfromsite + '/'

                order.sum_from_rub = round(
                    post_data['sum_from'] * rates.get(base=change.pay_from.usedmoney.usedmoney, profit='RUB').nominal_2 / rates.get(
                        base=change.pay_from.usedmoney.usedmoney, profit='RUB').nominal_1, 2)
                order.sum_to_rub = round(post_data['sum_to'] * rates.get(base='RUB', profit=change.pay_to.usedmoney.usedmoney).nominal_1 /
                                         rates.get(base='RUB', profit=change.pay_to.usedmoney.usedmoney).nominal_2, 2)
                order.fee = change.fee
                order.profit_rub = round(order.sum_from_rub - order.sum_to_rub, 2)
                order.rate = rates.get(base=change.pay_from.usedmoney.usedmoney,
                                       profit=change.pay_to.usedmoney.usedmoney)
                # это не прибыль, так как здесь ещё включены комиссии
                order.profit = round(post_data['sum_from'] * rates.get(base=change.pay_from.usedmoney.usedmoney,
                                                                       profit=change.pay_to.usedmoney.usedmoney).nominal_2 /
                                     rates.get(base=change.pay_from.usedmoney.usedmoney,
                                               profit=change.pay_to.usedmoney.usedmoney).nominal_1 -
                                     post_data['sum_to'], 8 if change.pay_to.moneytype.moneytype == 'crypto' else 2)
                '''
                partner
                partner_rub
                rate_best
                rate_cb
                '''
                order.save()
            else:
                if order_model[0].status == 'cancel':
                    return render(request, 'cancel.html', {'order_num': order_model[0].num})

            if self.get_order_for_bd(request, left, right, idfromsite)[0]:
                if change.pay_from.moneytype.moneytype == 'crypto':
                    return render(request, 'confirm_crypto.html', self.context)
                return render(request, 'confirm.html', self.context)
            else:
                return render(request, 'order_not_found.html')
        elif request.POST.get('checkinput', '0') == 'Оплатить':
            print('нажали кнопку Оплатить')
            pass
        elif request.POST.get('checkinput', '0') == 'Отменить':
            order_model = OrderModel.objects.filter(numuuid=idfromsite, pay_from__code=left, pay_to__code=right)
            if order_model.count() != 1:
                return render(request, 'order_not_found.html')
            order_model = order_model[0]
            if order_model.status != 'cancel':
                order_model.status = 'cancel'
                order_model.data_change = now()
                order_model.save()
            return render(request, 'cancel.html', {'order_num': order_model.num})
        else:
            return render(request, 'error.html', {'error': 'Что то пошло не так. Код ошибки: 101'})

# class ChangeView(View):
#     context = {}
#
#     def CancelChange(self):
#         pass
#
#     def get(self, request, left, right, idfromsite):
#         print('Меняем ? get')
#         order_model = OrderModel.objects.filter(numuuid=idfromsite, pay_from__code=left, pay_to__code=right)
#         if order_model.count() != 1:
#             return render(request, 'order_not_found.html', self.context)
#         order_model = order_model[0]
#         if order_model.status == 'cancel':
#             return render(request, 'cancel.html', {'order_num': order_model.num})
#
#         # temp = request.POST['solution']
#         # if temp == 'Оплатить':
#         #     print('Оплатить заявку')
#         # else:  # отменть заявку
#         #     # order_model.status = 'cancel'
#         #     # order_model.data_change = now()
#         #     # order_model.save()
#         #     return render(request, 'cancel.html', {'order_num': order_model.num})
#
#         return render(request, 'change.html', self.context)
#
#     def post(self, request, left, right, idfromsite):
#         order_model = OrderModel.objects.filter(numuuid=idfromsite, pay_from__code=left, pay_to__code=right)
#         if order_model.count() != 1:
#             return render(request, 'order_not_found.html', self.context)
#         order_model = order_model[0]
#
#         temp = request.POST['solution']
#         if temp == 'Оплатить':
#             print('Оплатить заявку')
#         else:  # отменть заявку
#             order_model.status = 'cancel'
#             order_model.data_change = now()
#             order_model.save()
#             return render(request, 'cancel.html', {'order_num': order_model.num})
#
#         return render(request, 'change.html', self.context)
