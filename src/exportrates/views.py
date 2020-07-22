from django.http import HttpResponse
from src.change.models import ChangeModel
import xml.etree.ElementTree as xml
from src.parsers.models import AllRates


# todo думаю можно отдачу xml соеденить с отдачей json по api. Многие расчёты повторяются. Проверка курса обмена в
#  заявке тоже считает те же самые данные


def xmlrts(request):
    change = ChangeModel.objects.filter(site__url__icontains=request.headers['Host'])
    rates = AllRates.objects.all()

    root_element = xml.Element('rates')

    for i in change:
        if i.active and i.pay_from.active and i.pay_to.active_out and i.pay_to.active and (
                i.pay_from.reserve < i.pay_from.max_balance):
            item_element = xml.Element('item')
            root_element.append(item_element)

            # создаем дочерние суб-элементы.
            from_element = xml.SubElement(item_element, 'from')
            from_element.text = i.pay_from.code

            to_element = xml.SubElement(item_element, 'to')
            to_element.text = i.pay_to.code

            # тип платёжек нужен для округления
            ltype = i.pay_from.moneytype.moneytype
            rtype = i.pay_from.moneytype.moneytype

            base_money = i.pay_from.usedmoney.usedmoney
            profit_money = i.pay_to.usedmoney.usedmoney
            left = 1
            right = 1
            if base_money != profit_money:
                left = rates.get(base=base_money, profit=profit_money).nominal_1
                right = rates.get(base=base_money, profit=profit_money).nominal_2

            fee = right * i.fee / 100 + i.fee_fix
            fee = round(fee, 8 if ltype == 'crypto' else 2)
            if i.fee_min > 0:
                fee = max(fee, i.fee_min)
            if i.fee_max > 0:
                fee = min(fee, i.fee_max)

            in_element = xml.SubElement(item_element, 'in')
            in_element.text = str(left)

            out_element = xml.SubElement(item_element, 'out')
            out_element.text = str(right - fee)

            amount_element = xml.SubElement(item_element, 'amount')
            amount_element.text = str(i.pay_to.reserve_for_site)

            # fromfee_element = xml.SubElement(item_element, 'fromfee')
            # fromfee_element.text = '330'
            #
            # tofee_element = xml.SubElement(item_element, 'tofee')
            # tofee_element.text = '300'

            minamount_element = xml.SubElement(item_element, 'minamount')
            temp = max(i.pay_from_min, left / right * i.pay_to_min)
            temp = round(temp, 8 if ltype == 'crypto' else 2)
            minamount_element.text = str(temp) + ' ' + i.pay_from.usedmoney.usedmoney

            maxamount_element = xml.SubElement(item_element, 'maxamount')
            temp = min(i.pay_from_max, left / right * min(i.pay_to_max, i.pay_to.reserve))
            temp = round(temp, 8 if ltype == 'crypto' else 2)
            maxamount_element.text = str(temp) + ' ' + i.pay_from.usedmoney.usedmoney

            prm = []
            if i.manual:
                prm.append('manual')
            else:
                if ((len(i.pay_from.code) >= 7) and i.pay_from.code.startswith('CASH')) or (
                        (len(i.pay_to.code) >= 7) and i.pay_to.code.startswith('CASH')):
                    prm.append('manual')

            if i.juridical:
                prm.append('juridical')
            if i.verifying:
                prm.append('verifying')
            if i.cardverify:
                prm.append('cardverify')
            if i.floating:
                prm.append('floating')
            if i.otherin:
                prm.append('otherin')
            if i.otherout:
                prm.append('otherout')
            if i.reg:
                prm.append('reg')

            if len(i.pay_from.code) >= 7 and i.pay_from.code.startswith('CARD'):
                if i.card2card:
                    prm.append('card2card')

            prm_str = ','.join(prm)
            if prm_str != '':
                param_element = xml.SubElement(item_element, 'param')
                param_element.text = prm_str

            # todo город для наличного обмена может быть не 1, а несколько. Пока расчёт на 1 город
            if len(i.pay_from.code) >= 7 and i.pay_from.code.startswith('CASH'):
                city_element = xml.SubElement(item_element, 'city')
                city_element.text = i.city_change.name
            else:
                if len(i.pay_to.code) >= 7 and i.pay_to.code.startswith('CASH'):
                    city_element = xml.SubElement(item_element, 'city')
                    city_element.text = i.city_change.name

    return HttpResponse(xml.tostring(root_element, method='xml', encoding='utf8'), content_type='text/xml')
