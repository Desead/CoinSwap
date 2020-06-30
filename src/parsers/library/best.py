# todo с загрузкой, разархивированием и последующим чтением может быть масса ошибок. Надо всё предусмотреть
#  и возможное обернуть в ислючения
import io
import os
import zipfile
import requests

loadpath = 'bsinfo/'


def loadFiles():
    responce = requests.get('http://api.bestchange.ru/info.zip')
    if responce.status_code == 200:
        zf = zipfile.ZipFile(io.BytesIO(responce.content))
        zf.extractall(loadpath)
        return 0
    if responce.status_code != 200:
        print('Ошибка загрузки info.zip с беста')
        return -1


def getData(fname, pos):
    dict_out = {}
    filename = loadpath + fname
    if os.path.isfile(filename):
        with open(filename, encoding='cp1251') as fl:
            for row in fl:
                temp = row.split(';')
                if temp[0].isdecimal() and temp[pos] != '':
                    x = int(temp[0])
                    dict_out[x] = temp[pos]
                else:
                    continue
    return dict_out


# todo Данные надо писать в базу не по строкам а сразу целым фреймом
def getRates():
    list_out = []
    filename = loadpath + 'bm_rates.dat'
    if os.path.isfile(filename):
        with open(filename, encoding='utf-8') as fl:
            for row in fl:
                temp = row.split(';')
                ls = []
                for i in range(6):
                    ls.append(temp[i])
                list_out.append(ls)
    return list_out
