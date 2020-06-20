import requests
import xml.etree.ElementTree as ET
from src.core.models import UsedMoneyModel


def get_cbrf():
    # todo если один из адресов не работает то пробуем второй. По уму наверное надо сделать 2 попытки и если оба адреса
    #  не отвечают то через слип попробовать ещё раз и потом уже вывести сообщение в админку
    response = requests.get('http://www.cbr.ru/scripts/XML_daily.asp')
    if response.status_code != 200:
        response = requests.get('https://www.cbr-xml-daily.ru/daily.xml')
        if response.status_code != 200:
            return -1, 'Ошибка парсера ЦБ '

    tree = ''
    try:
        tree = ET.fromstring(response.text)
    except:
        return -1, 'Ошибка парсинга XML'

    # отслеживаемые валюты, другие не загружаем
    bd = UsedMoneyModel.objects.all()
    Base = []
    for i in bd:
        Base.append(str(i))

    Profit = 'RUB'

    temp = {}

    for child in tree:
        if child[1].text.upper() in Base:
            temp[child[1].text + Profit] = [
                int(child[2].text),
                float(child[4].text.replace(',', '.')),
                child[1].text,
                Profit,
                'ЦБРФ'
            ]
            # разворачиваем курсы и пары для получения реверса
            temp[Profit + child[1].text] = [
                float(child[4].text.replace(',', '.')),
                int(child[2].text),
                Profit,
                child[1].text,
                'ЦБРФ Reverse'
            ]
    # есть начальные курсы и реверс строим все оставшиеся кроссы
    money = set()  # получаем список всех валют
    for v in temp.values():
        money.add(v[2])
        money.add(v[3])

    # строим все возможные комбинации
    rates = {}
    for i in money:
        for j in money:
            if i == j:
                continue  # пропускаем обмен самой на себя
            if i + j in temp:
                continue  # пропускаем уже существующие обмены
            rates[i + j] = [temp[i + Profit][0], temp[i+Profit][1] / temp[Profit + j][0] * temp[Profit+j][1], i, j,
                            'ЦБРФ Calc']

    temp.update(rates)

    return 0, temp
