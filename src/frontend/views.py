from django.contrib.auth.models import User
from django.shortcuts import render
from django.utils.timezone import now
from django.views.generic.base import View
from src.change.models import OrderModel, ChangeModel
from src.change.forms import HTMLform
from src.core.models import PaySystemModel, SiteModel
from src.frontend.library import addfunc


class StartView(View):
    context = {}

    def get(self, request):
        # form = OrderModelForm()
        # todo можно проверить платёжки на их наличие и если их нету выдать 404 ,также можно проверить длинну
        #  названия платёжки чтобы не писали туда лишнего. оформить в функицю т.к. ниже надо тоже самое

        x = request.path.strip('/').split('/')  # получии платёжки которые участвют в обмене

        # self.context['direction'] = ChangeModel.objects.filter(active=True)
        return render(request, 'index.html', self.context)


class ConfirmView(View):
    """ Коды ошибок
    100 - Не найден обмен с указанными платёжками
    101 -
    102 - Указанный статус заявки отсутствует
    103 - нет параметра test_num. значит не вызывалась js функция rates.
    104 - test_num не число
    105,106 - полученный код платёжки состоит не только из заглавных букв
    107 - uuid странный
    108,109 - отдаваемая, получаемая сумма <= 0
    110 - неверный sumlock
    111 - неверный номер телефона
    112 - номер обмена передали неверно
    113 - неверная почта
    115,114 - клиентом указаны неверные кошельки
    116 - что то не так с дополнительным полем для крипты
    """

    # todo сраницу order_not_found сделать более информативной ?
    context = {}

    # берём данные заявки из бд и заполняем их в словарь для вывода
    def get_order_for_bd(self, request, left, right, idfromsite):
        order_model = OrderModel.objects.filter(numuuid=idfromsite, pay_from__code=left, pay_to__code=right)
        if order_model.count() != 1:
            return False
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
        return True

    def get(self, request, left, right, idfromsite):
        if self.get_order_for_bd(request, left, right, idfromsite):
            return render(request, 'confirm.html', self.context)
        else:
            return render(request, 'order_not_found.html')

    def post(self, request, left, right, idfromsite):

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

        fee_client = addfunc.str2float(request.POST.get('fee_client', '0'))

        nmphone = addfunc.str2int(request.POST.get('nmphone', '11111111111'))
        if nmphone <= 0:
            return render(request, 'error.html', {'error': 'Что то пошло не так. Код ошибки: 111'})

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

        text = ChangeModel.objects.filter(active=True, pay_from__code=left, pay_to__code=right, pk=test_num)
        if text.count() != 1:
            return render(request, 'error.html', {'error': 'Что то пошло не так. Код ошибки: 100'})
        if text[0].manual:
            text = text[0].text
        else:
            text = ''

        order_model = OrderModel.objects.filter(numuuid=idfromsite, pay_from__code=left, pay_to__code=right)

        if not order_model.exists():  # если такой записи нет то создаём её
            order = OrderModel()
            order.sum_from = sum_from
            order.sum_to = sum_to
            order.wallet_client_from = wallet_client_from
            order.wallet_client_to = wallet_client_to
            order.wallet_add = wallet_add
            order.fee_client = fee_client
            order.lock = sumlock
            order.pay_from = PaySystemModel.objects.get(code=left)
            order.pay_to = PaySystemModel.objects.get(code=right)
            order.wallet_exchange_to = wallet_client_from
            order.wallet_exchange_from = wallet_client_to
            # todo не работает выбор пользователя
            order.client = list(User.objects.all())[0]
            order.num = 100 + OrderModel.objects.all().count()
            # todo не работает выбор сайта
            order.site = list(SiteModel.objects.all())[0]
            order.data_create = now()
            order.data_change = now()
            order.numuuid = idfromsite
            order.text = text
            order.save()

        if self.get_order_for_bd(request, left, right, idfromsite):
            return render(request, 'confirm.html', self.context)
        else:
            return render(request, 'order_not_found.html')
