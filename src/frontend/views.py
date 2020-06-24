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

    # если ид не найдено то такая заявка не существует
    def get(self, request, left, right, idfromsite):
        temp = OrderModel.objects.filter(numuuid=idfromsite, pay_from__code=left, pay_to__code=right)
        if temp.count() != 1:
            return render(request, 'order_not_found.html')

        # todo статус заявки пока не передаётся
        context = {'left': temp[0].pay_from.screen,
                   'right': temp[0].pay_to.screen,
                   'sum_from': temp[0].sum_from,
                   'sum_to': temp[0].sum_to,
                   'wallet_client_to': temp[0].wallet_client_to,
                   'wallet_client_from': temp[0].wallet_client_from,
                   'num': temp[0].num,
                   'date_create': temp[0].data_create.strftime('%Y/%m/%d %H:%M:%S'),
                   'type': temp[0].pay_from.moneytype.moneytype,
                   'type_freeze': temp[0].pay_from.moneytype.freeze,
                   'type_freeze_confirm': temp[0].pay_from.moneytype.freeze_confirm,
                   'text': temp[0].text,
                   'status': temp[0].status,
                   }

        return render(request, 'confirm.html', context)

    # todo django всё экранирует, но тем не менее надо вставить свои проверки тоже, чтобы не полагаться не понятно на что
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

        # todo если крипте требуется доп.поле то проверяем, также в js на фронте надо вставить эту же проверку.
        if (right == 'EOS') or (right == 'XRP'):
            if wallet_add == '':
                return render(request, 'error.html', {'error': 'add wallet = " "'})
            if len(wallet_add) > 50:
                return render(request, 'error.html', {'error': 'add wallet  very long'})

        text = ChangeModel.objects.filter(active=True, pay_from__code=left, pay_to__code=right, pk=test_num)
        if text.count() != 1:
            return render(request, 'error.html', {'error': 'Что то пошло не так. Код ошибки: 100'})
        text = text[0].text

        temp = OrderModel.objects.filter(numuuid=idfromsite, pay_from__code=left, pay_to__code=right)

        if not temp.exists():  # если такой записи нет то создаём её
            # todo делаем проверку курса обмена и после, если всё ок создаём заявку

            # записываем в бд после проверки
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

            temp = OrderModel.objects.get(numuuid=idfromsite)

            context = {'left': left,
                       'right': right,
                       'sum_from': sum_from,
                       'sum_to': sum_to,
                       'wallet_client_to': wallet_client_to,
                       'wallet_client_from': wallet_client_from,
                       'wallet_add': wallet_add,
                       'num': temp.num,
                       'date_create': temp.data_create.strftime('%Y/%m/%d %H:%M:%S'),
                       'type': PaySystemModel.objects.get(code=left).moneytype.moneytype,
                       'type_freeze': PaySystemModel.objects.get(code=left).moneytype.freeze,
                       'type_freeze_confirm': PaySystemModel.objects.get(code=left).moneytype.freeze_confirm,
                       'text': text,
                       'status': 'Новая заявка',  # todo вписать статус новой заявки из кортежа, а не напрямую
                       }
        else:  # если запись есть то получаем её данные и выводим их ,а не создаём новую заявку
            # todo если статус заявки не новая то таймер js включать не надо
            order_status = ''
            for i in temp[0].STATUS_CHOISES:
                if i[0] == temp[0].status:
                    order_status = i[1]
                    break
            else:
                return render(request, 'error.html', {'error': 'Что то пошло не так. Код ошибки: 102'})

            context = {'left': temp[0].pay_from.screen,
                       'right': temp[0].pay_to.screen,
                       'sum_from': temp[0].sum_from,
                       'sum_to': temp[0].sum_to,
                       'wallet_client_to': temp[0].wallet_client_to,
                       'wallet_client_from': temp[0].wallet_client_from,
                       'num': temp[0].num,
                       'date_create': temp[0].data_create.strftime('%Y/%m/%d %H:%M:%S'),
                       'type': temp[0].pay_from.moneytype.moneytype,
                       'type_freeze': temp[0].pay_from.moneytype.freeze,
                       'type_freeze_confirm': temp[0].pay_from.moneytype.freeze_confirm,
                       'text': temp[0].text,
                       'status': order_status,
                       }

        return render(request, 'confirm.html', context)
