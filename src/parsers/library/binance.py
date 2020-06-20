import requests, json
from ..models import UsedMoneyModel


def getRates():
    url_pirce = 'https://api.binance.com/api/v3/ticker/price'
    url_data = 'https://api.binance.com/api/v3/exchangeInfo'

    # отслеживаемые валюты. Заглавными буквами.
    bd = UsedMoneyModel.objects.all()
    temp = []
    for i in bd:
        temp.append(str(i).upper())

    # из начальных валют составляем множество возможных пар, курсы которых нам интересны
    need = set()
    for i in temp:
        for j in temp:
            if i == j:
                continue
            need.add(i + j)
            need.add(j + i)

    dist_out = {}

    # todo получать курс надо часто, а данные о парах можно получать намного реже. Надо вынести эту функцию
    #  в отдельный крон с периодом раз в несколько дней наверное. либо можно оптимизовать - сначала пройтись
    #  и убрать все ненужные пары а потом уже с отсатка снимать данные
    res_data = requests.get(url_data)
    if res_data.status_code != 200:
        return -1, 'Ошибка получения данных с Binance'

    res_price = requests.get(url_pirce)
    if res_price.status_code != 200:
        return -1, 'Ошибка получения курсов с Binance'

    res_data = json.loads(res_data.text)['symbols']
    res_price = json.loads(res_price.text)

    for i in res_price:
        if i['symbol'] in need:
            for j in res_data:
                if j['symbol'] == i['symbol']:
                    temp = []
                    temp.append(1)
                    temp.append(float(i['price']))
                    temp.append(j['baseAsset'])
                    temp.append(j['quoteAsset'])
                    temp.append('Binance')
                    dist_out[i['symbol']] = temp

                    # разворачиваем курсы и пары для получения реверса
                    temp = []
                    temp.append(float(i['price']))
                    temp.append(1)
                    temp.append(j['quoteAsset'])
                    temp.append(j['baseAsset'])
                    temp.append('Binance Reverse')
                    dist_out[j['quoteAsset'] + j['baseAsset']] = temp

    # есть начальные курсы и реверс строим все оставшиеся кроссы
    money = set()  # получаем список всех валют
    for v in dist_out.values():
        money.add(v[2])
        money.add(v[3])

    # строим все возможные комбинации
    rates = {}
    for i in money:
        for j in money:
            if i == j:
                continue  # пропускаем обмен самой на себя
            if i + j in dist_out:
                continue  # пропускаем уже существующие обмены
            rates[i + j] = [0, 0, i, j, 'Binance Calc']

    # внвоь проходим по словарю rates в поисках третьей валюты с которой есть пара и дял базы и для профита
    for k, v in rates.items():
        for Profit in money:
            if Profit == v[2] or Profit == v[3]:
                continue  # не ищем самих себя
            if v[2] + Profit in dist_out:
                if Profit + v[3] in dist_out:  # вот наша промежуточная пара
                    for m in range(3):  # цикл для лучшей точности, чтобы не получалось значений 0.0000013423
                        x = 10 ** m
                        rates[k][0] = x * (dist_out[v[2] + Profit][0])
                        rates[k][1] = x * (dist_out[v[2] + Profit][1]) / dist_out[Profit + v[3]][0] * \
                                      dist_out[Profit + v[3]][
                                          1]
                        if (rates[k][0] >= 0.01) and (rates[k][1] >= 0.01):
                            break
                    break

    dist_out.update(rates)

    return dist_out
