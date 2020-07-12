from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.timezone import now
from django.views.generic.base import View
from src.change.models import OrderModel, ChangeModel
from src.core.models import PaySystemModel, SiteModel
from src.frontend.library import addfunc
from src.parsers.models import AllRates


class StartView(View):

    def get(self, request):

        queryset_site = SiteModel.objects.filter(url__icontains=request.headers['Host'])
        if queryset_site.count() != 1:
            return HttpResponse('Сайт не найден')

        queryset_order = OrderModel.objects.filter(site__url__icontains=request.headers['Host'], status='ok')[:3]
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
        context['order'] = queryset_order[0].num

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
    101 -
    102 - Указанный статус заявки отсутствует
    103 - нет параметра test_num. значит не вызывалась js функция rates.
    104 - test_num не число
    105,106 - полученный код платёжки не найден
    1050,1060 - Платёжки не активны
    1061 - С платёжки нельзя отдавать
    107 - uuid странный
    108,109 - отдаваемая, получаемая сумма <= 0
    110 - неверный sumlock
    111 - неверный номер телефона
    112 - номер обмена передали неверно
    113 - неверная почта
    115,114 - клиентом указаны неверные кошельки
    116 - что то не так с дополнительным полем для крипты
    117 -
    118 - не попали в мин\макс
    """

    context = {}

    # todo если в action вставили другие платёжки, которые тоже есть?

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
        return True, order_model.status, order_model.num

    # проверяем данные переданные в адресной строке
    def check_adress_data(self, request, left, right, idfromsite, queryset):

        # проверили наличие плаёжки и разршение их использования
        temp = queryset.filter(code=left)
        if temp.count() != 1:
            return False, '105'
        if not temp.active:
            return False, '1050'

        temp = queryset.filter(code=right)
        if temp.count() != 1:
            return False, '106'
        if not temp.active:
            return False, '1060'
        if not temp.active_out:
            return False, '1061'

        if addfunc.check_uuid(idfromsite) == '':
            return False, '107'

        return True,

    def get(self, request, left, right, idfromsite):
        temp = self.get_order_for_bd(request, left, right, idfromsite)
        if temp[0]:
            if temp[1] == 'cancel':
                return render(request, 'cancel.html', {'order_num': temp[2]})
            return render(request, 'confirm.html', self.context)
        else:
            return render(request, 'order_not_found.html')

    def post(self, request, left, right, idfromsite):

        queryset_PaySystemModel = PaySystemModel.objects.all()
        temp = self.check_adress_data(request, left, right, idfromsite, queryset_PaySystemModel)
        if temp[0] == False:
            return render(request, 'error.html', {'error': 'Что то пошло не так. Код ошибки: ' + temp[1]})

        # проверим то что пришло в адресной строке: left, right, idfromsite
        if addfunc.check_pscode(left) == '':
            return render(request, 'error.html', {'error': 'Что то пошло не так. Код ошибки: 105'})
        if addfunc.check_pscode(right) == '':
            return render(request, 'error.html', {'error': 'Что то пошло не так. Код ошибки: 106'})
        if addfunc.check_uuid(idfromsite) == '':
            return render(request, 'error.html', {'error': 'Что то пошло не так. Код ошибки: 107'})

        # проверим данные из POST запроса
        sum_from = addfunc.str2float(request.POST.get('sum_from', '0'))
        if sum_from <= 0:
            return render(request, 'error.html', {'error': 'Что то пошло не так. Код ошибки: 108'})

        sum_to = addfunc.str2float(request.POST.get('sum_to', '0'))
        if sum_to <= 0:
            return render(request, 'error.html', {'error': 'Что то пошло не так. Код ошибки: 109'})

        sumlock = addfunc.check_sumlock(request.POST.get('sumlock', ''))
        if sumlock == '':
            return render(request, 'error.html', {'error': 'Что то пошло не так. Код ошибки: 110'})

        fee_client = max(addfunc.str2float(request.POST.get('fee_client', '0')), 0)

        nmphone = addfunc.str2int(request.POST.get('nmphone', '11111111111'))
        if nmphone <= 0:
            return render(request, 'error.html', {'error': 'Что то пошло не так. Код ошибки: 111'})

        # todo test_num можно проверить на соответствие номера запроса и названия платёжек слева и справа. есть ои такое совпадение
        test_num = addfunc.str2int(request.POST.get('test_num', ''))
        if test_num <= 0:
            return render(request, 'error.html', {'error': 'Что то пошло не так. Код ошибки: 112'})

        nmmail = addfunc.check_mail(request.POST.get('nmmail', 'clear@m.ru'))
        if nmmail == '':
            return render(request, 'error.html', {'error': 'Что то пошло не так. Код ошибки: 113'})

        # todo как проверить кошельки И дополнительное поле для крипты?
        wallet_client_from = request.POST.get('wallet_client_from', False)
        if wallet_client_from:
            if addfunc.check_wallet(wallet_client_from) == '':
                return render(request, 'error.html', {'error': 'Что то пошло не так. Код ошибки: 114'})

        wallet_client_to = request.POST.get('wallet_client_to', False)
        if wallet_client_to:
            if addfunc.check_wallet(wallet_client_to) == '':
                return render(request, 'error.html', {'error': 'Что то пошло не так. Код ошибки: 115'})

        wallet_add = request.POST.get('wallet_add', False)
        if wallet_add:
            if addfunc.check_wallet_add(wallet_add) == '':
                return render(request, 'error.html', {'error': 'Что то пошло не так. Код ошибки: 116'})

        # todo если крипте требуется доп.поле то проверяем, также в js надо вставить эту же проверку.
        if (right == 'EOS') or (right == 'XRP'):
            if wallet_add == '':
                return render(request, 'error.html', {'error': 'add wallet = " "'})
            if len(wallet_add) > 50:
                return render(request, 'error.html', {'error': 'add wallet  very long'})

        change = ChangeModel.objects.filter(active=True, pay_from__code=left, pay_to__code=right, pk=test_num)
        text = ''
        if change.count() != 1:
            return render(request, 'error.html', {'error': 'Что то пошло не так. Код ошибки: 100'})
        change = change[0]
        if change.manual:
            text = change.text

        order_model = OrderModel.objects.filter(numuuid=idfromsite, pay_from__code=left, pay_to__code=right)

        # проверем корректность сумм для обмена Всё пересчитываем

        rates = AllRates.objects.all()

        if sumlock == 'sumtolock':
            temp = (sum_to + change.fee_fix + fee_client) * 100 / (100 - change.fee)
            temp = round(temp - sum_to, 8 if change.pay_to.moneytype.moneytype == 'crypto' else 2)
            temp = max(temp, change.fee_min)
            temp = temp + sum_to
            sum_from = round(temp * rates.get(base=change.pay_from.usedmoney.usedmoney,
                                              profit=change.pay_to.usedmoney.usedmoney).nominal_1 / rates.get(
                base=change.pay_from.usedmoney.usedmoney, profit=change.pay_to.usedmoney.usedmoney).nominal_2,
                             8 if change.pay_from.moneytype.moneytype == 'crypto' else 2)
        else:
            # посчитали сумму которую нужно отдать просто по курсу обмена
            out_money = round(sum_from * rates.get(base=change.pay_from.usedmoney.usedmoney,
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

            sum_to = round(max(out_money - fee - fee_client, 0),
                           8 if change.pay_to.moneytype.moneytype == 'crypto' else 2)

        # проверяем полученные суммы обмена на попадание в границы мин и макс
        if (sum_from < change.pay_from_min) or (sum_from > change.pay_from_max) or (sum_to < change.pay_to_min) or (
                sum_to > change.pay_to_max):
            return render(request, 'error.html', {'error': 'Что то пошло не так. Код ошибки: 118'})

        if not order_model.exists():  # если такой записи нет то создаём её
            order = OrderModel()
            order.sum_from = sum_from
            order.sum_to = sum_to
            order.wallet_client_from = wallet_client_from
            order.wallet_client_to = wallet_client_to
            order.wallet_exchange_to = wallet_client_from
            order.wallet_exchange_from = wallet_client_to
            order.wallet_add = wallet_add
            order.fee_client = fee_client
            order.lock = 'to' if sumlock == 'sumtolock' else 'from'
            order.pay_from = PaySystemModel.objects.get(code=left)
            order.pay_to = PaySystemModel.objects.get(code=right)
            # todo не работает выбор пользователя и сайта
            order.client = list(User.objects.all())[0]
            order.num = 100 + OrderModel.objects.all().count()
            # order.site = SiteModel.objects.filter(url__icontains=request.headers['Host'])
            order.site = list(SiteModel.objects.all())[0]
            order.data_create = order.data_change = now()
            order.numuuid = idfromsite
            order.text = text
            order.url_change = request.headers['Origin'] + '/' + left + '/' + right + '/' + idfromsite + '/'

            order.sum_from_rub = round(
                sum_from * rates.get(base=change.pay_from.usedmoney.usedmoney, profit='RUB').nominal_2 / rates.get(
                    base=change.pay_from.usedmoney.usedmoney, profit='RUB').nominal_1, 2)
            order.sum_to_rub = round(
                sum_to * rates.get(base='RUB', profit=change.pay_to.usedmoney.usedmoney).nominal_1 / rates.get(
                    base='RUB', profit=change.pay_to.usedmoney.usedmoney).nominal_2, 2)
            order.fee = change.fee
            order.profit_rub = round(order.sum_from_rub - order.sum_to_rub, 2)

            order.rate = rates.get(base=change.pay_from.usedmoney.usedmoney, profit=change.pay_to.usedmoney.usedmoney)
            # это не прибыль, так как здесь ещё включены комиссии
            order.profit = round(sum_from * rates.get(base=change.pay_from.usedmoney.usedmoney,
                                                      profit=change.pay_to.usedmoney.usedmoney).nominal_2 / rates.get(
                base=change.pay_from.usedmoney.usedmoney, profit=change.pay_to.usedmoney.usedmoney).nominal_1 - sum_to,
                                 8 if change.pay_to.moneytype.moneytype == 'crypto' else 2)
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


class ChangeView(View):
    context = {}

    def CancelChange(self):
        pass

    def get(self, request, left, right, idfromsite):
        print('Меняем ? get')
        order_model = OrderModel.objects.filter(numuuid=idfromsite, pay_from__code=left, pay_to__code=right)
        if order_model.count() != 1:
            return render(request, 'order_not_found.html', self.context)
        order_model = order_model[0]
        if order_model.status == 'cancel':
            return render(request, 'cancel.html', {'order_num': order_model.num})

        # temp = request.POST['solution']
        # if temp == 'Оплатить':
        #     print('Оплатить заявку')
        # else:  # отменть заявку
        #     # order_model.status = 'cancel'
        #     # order_model.data_change = now()
        #     # order_model.save()
        #     return render(request, 'cancel.html', {'order_num': order_model.num})

        return render(request, 'change.html', self.context)

    def post(self, request, left, right, idfromsite):
        order_model = OrderModel.objects.filter(numuuid=idfromsite, pay_from__code=left, pay_to__code=right)
        if order_model.count() != 1:
            return render(request, 'order_not_found.html', self.context)
        order_model = order_model[0]

        temp = request.POST['solution']
        if temp == 'Оплатить':
            print('Оплатить заявку')
        else:  # отменть заявку
            order_model.status = 'cancel'
            order_model.data_change = now()
            order_model.save()
            return render(request, 'cancel.html', {'order_num': order_model.num})

        return render(request, 'change.html', self.context)
