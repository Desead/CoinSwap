import os
import random

from django.shortcuts import render
from django.utils.datetime_safe import datetime
from django.views.generic import ListView
from django.views.generic.base import View

from CoinSwap.settings import BASE_DIR
from .forms import CBRFForm
from .models import UsedMoneyModel, MoneyTypeModel, PaySystemModel, SiteModel
from ..change.models import ChangeModel
from ..parsers.library import cbrf, binance
from ..parsers.library import best
from ..parsers.models import CBRF, Binance, AllRates
import csv


def CBRFFormView(request):
    form = CBRFForm()
    context = {'cbrfform': form}
    return render(request, 'core/info.html', context)


class Order(ListView):
    queryset = {}
    template_name = 'core/orders.html'


class PaySystems(ListView):
    queryset = {}
    template_name = 'core/paysystem.html'


class Change(ListView):
    queryset = {}
    template_name = 'core/change.html'


class Info(ListView):
    queryset = {}
    template_name = 'core/info.html'


class Cbrf(View):
    context = {}

    def get(self, request):
        CBRF.objects.all().delete()
        temp = cbrf.get_cbrf()
        if temp[0] == 0:
            for k, v in temp[1].items():
                a = CBRF()
                a.name = k
                a.nominal_1 = v[0]
                a.nominal_2 = v[1]
                a.base = v[2]
                a.profit = v[3]
                a.dt = datetime.now()
                a.source = v[4]
                a.save()

        self.context['cbrf'] = CBRF.objects.all()

        return render(request, 'core/cbrf.html', self.context)


class Bin(View):
    context = {}

    def get(self, request):
        temp = binance.getRates()
        Binance.objects.all().delete()
        for k, v in temp.items():
            a = Binance()
            a.name = k
            a.nominal_1 = v[0]
            a.nominal_2 = v[1]
            a.base = v[2]
            a.profit = v[3]
            a.source = v[4]
            a.dt = datetime.now()
            a.save()

        self.context['binance'] = Binance.objects.all()

        return render(request, 'core/binance.html', self.context)


class Rates(View):
    context = {}

    # todo объединение двух моделей надо переделать. Должно быть какое то объединение ,чтобы не в цикле
    #  перебирать элементы. Возможно есть смысл сразу писать в эту таблицу а не в промежуточные
    def get(self, request):
        AllRates.objects.all().delete()
        rates = {}  # словарь со всеми курсами. сначала взяли известные из бд, потом добавим остальные
        bin = Binance.objects.all()
        cb = CBRF.objects.all()
        a = [bin, cb]
        for i in a:
            for j in i:
                rates[j.name] = [
                    j.nominal_1,
                    j.nominal_2,
                    j.base,
                    j.profit,
                    j.dt,
                    j.source
                ]

        # теперь рассчитаем все оставшиеся кроссы
        money = UsedMoneyModel.objects.all()
        # todo в список обмена нужно выставлять только те пары, для которых есть курс обмена!
        # выстраиваем все комбинации
        for i in money:
            for j in money:
                if i == j:
                    continue
                if i.usedmoney + j.usedmoney in rates:
                    continue
                # создали новую пару, теперь ищём третью валюту через которую их можем соеденить
                for k in money:
                    if i.usedmoney + k.usedmoney in rates:
                        if k.usedmoney + j.usedmoney in rates:
                            # нашли такой вариант
                            rates[i.usedmoney + j.usedmoney] = [
                                rates[i.usedmoney + k.usedmoney][0],
                                # todo когда формируются курсы надо вставить проверку на 0 и на другие исключения
                                rates[i.usedmoney + k.usedmoney][1] / rates[k.usedmoney + j.usedmoney][0] *
                                rates[k.usedmoney + j.usedmoney][1],
                                i.usedmoney,
                                j.usedmoney,
                                rates[i.usedmoney + k.usedmoney][4],
                                'Calc'
                            ]
                            # сразу сделали реверс
                            rates[j.usedmoney + i.usedmoney] = [
                                rates[i.usedmoney + j.usedmoney][1],
                                rates[i.usedmoney + j.usedmoney][0],
                                j.usedmoney,
                                i.usedmoney,
                                rates[i.usedmoney + k.usedmoney][4],
                                'Calc Reverse'
                            ]
                            break
        for k, v in rates.items():
            a = AllRates()
            a.name = k
            a.nominal_1 = v[0]
            a.nominal_2 = v[1]
            a.base = v[2]
            a.profit = v[3]
            a.dt = v[4]
            a.source = v[5]
            a.save()

        self.context['rates'] = AllRates.objects.all()
        return render(request, 'core/rates.html', self.context)


class Bestchange(ListView):
    queryset = {}
    template_name = 'core/bestchange.html'


class Begin(View):
    context = {}
    um = UsedMoneyModel.objects.all()

    # показываем список всех используемых валют
    def screen_all_money(self):
        self.context = {'usedmoney': []}
        self.um = UsedMoneyModel.objects.all()
        for i in self.um:
            self.context['usedmoney'].append(i.usedmoney)

    def get(self, request):
        if request.GET.get('addmoney'):
            money = set()
            for i in self.um:
                money.add(i.usedmoney)

            temp = str(request.GET.get('addmoney'))
            temp = temp.split(',')
            for i in range(len(temp)):
                temp[i] = temp[i].strip().upper()

            temp = set(temp)
            temp.difference_update(money)

            for i in temp:
                if len(i) < 3:
                    continue
                a = UsedMoneyModel()
                a.usedmoney = i
                a.save()

        if request.GET.get('delmoney'):
            if request.GET.get('delmoney') == '*':
                self.um.delete()
            else:
                temp = str(request.GET.get('delmoney'))
                temp = temp.split(',')
                for i in range(len(temp)):
                    temp[i] = temp[i].strip().upper()

                for i in temp:
                    UsedMoneyModel.objects.filter(usedmoney=i).delete()

        if request.GET.get('addtype'):
            MoneyTypeModel.objects.all().delete()
            # a = ['crypto', 'eps', 'code', 'bank', 'moneysend', 'cash', ]
            a = [{'crypto': ['Криптовалюта', 30, ]},
                 {'eps': ['Электронная ПС', 15, ]},
                 {'code': ['Код криптобиржи', 15, ]},
                 {'bank': ['Банковский перевод', 15, ]},
                 {'moneysend': ['Денежный перевод', 15, ]},
                 {'cash': ['Наличные', 120, ]}, ]
            for i in a:
                for k, v in i.items():
                    temp = MoneyTypeModel()
                    temp.moneytype = k
                    temp.description = v[0]
                    temp.freeze = v[1]
                    temp.save()

        if request.GET.get('addpay'):
            PaySystemModel.objects.all().delete()
            # получили id всех типов платёжок и развернули список в словарь для более быстрого поиска ид по типу
            temp = list(MoneyTypeModel.objects.values_list())
            idtype = {}
            for i in temp:
                idtype[i[1]] = i[0]

            # получили id всех используемых валют и развернули список в словарь для более быстрого поиска ид по названию
            temp = list(UsedMoneyModel.objects.values_list())
            basemoney = {}
            for i in temp:
                basemoney[i[1]] = i[0]

            # добавляем id валют. Данные беруться с парсера беста. Одинаковое поле - название валюты(поле описание)
            idb = best.getData('bm_cy.dat', 2)
            idb = dict(zip(idb.values(), idb.keys()))  # меняем местами ключи и значения

            # добавляем все сещуствующие коды валют. Они заранее прописаны в файле взятом с беста
            filename = os.path.join(BASE_DIR, 'src/parsers/library/paysystem.csv')
            with open(filename) as fl:
                if fl.readable():
                    reader = csv.DictReader(fl)
                    for line in reader:
                        temp = PaySystemModel()
                        temp.code = line['Код валюты']
                        # temp.name = line['Описание']
                        temp.screen = line['Описание']
                        temp.moneytype = MoneyTypeModel.objects.get(pk=idtype[line['Тип']])
                        try:
                            temp.usedmoney = UsedMoneyModel.objects.get(pk=basemoney[line['Базовая валюта']])
                        except:
                            temp.usedmoney = None
                        try:
                            temp.idbest = idb[line['Описание']]
                        except:
                            temp.idbest = None
                        temp.reserve = random.randint(100, 50000)
                        temp.save()

        if request.GET.get('addchange'):
            ChangeModel.objects.all().delete()
            temp = PaySystemModel.objects.filter(active=True, usedmoney__isnull=False)
            rates = AllRates.objects.all()
            st = SiteModel.objects.all()
            fromto = set()
            for i in range(30):
                a = ChangeModel()
                a.site = st[0]
                a.pay_from = random.choice(temp)
                a.pay_to = random.choice(temp)
                if a.pay_to == a.pay_from:
                    continue
                if a.pay_from.code + a.pay_to.code in fromto:  # повторно уже существующий обмен не создаём
                    continue
                fromto.add(a.pay_from.code + a.pay_to.code)

                rts = a.pay_from.usedmoney.usedmoney + a.pay_to.usedmoney.usedmoney
                if len(AllRates.objects.filter(
                        name=rts)) == 0:  # Если отсутствует существующий курс обмена то тоже не создаём направление обмена
                    continue

                a.pay_from_min = random.randint(1, 5)
                a.pay_from_max = random.randint(5, 155)
                a.pay_to_min = random.randint(1, 5)
                a.pay_to_max = random.randint(5, 155)
                a.fee = random.randint(1, 20)
                a.active = True
                a.save()

        return render(request, 'core/begin.html', self.context)
