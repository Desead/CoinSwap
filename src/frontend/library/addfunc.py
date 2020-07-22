def str2float(temp: str) -> float:
    try:
        return float(temp.replace(',', '.'))
    except:
        return 0


def str2int(temp: str) -> int:
    try:
        return int(temp)
    except:
        return 0


def test_phone(temp: str) -> int:
    x = str2int(temp)
    if x > 0:
        if (len(temp) < 9) or (len(temp) > 16):
            return 0
    return x


def check_uuid(temp) -> str:
    if temp[8] != temp[13] != temp[18] != temp[23] != '_':
        return ''
    temp = temp.replace('_', '')

    flag_num = False
    flag_lit = False
    flag_spec = False

    for i in temp:
        if (i >= '0') and (i <= '9'):
            flag_num = True
            continue
        if ((i >= 'a') and (i <= 'z')) or ((i >= 'A') and (i <= 'Z')):
            flag_lit = True
            continue
        flag_spec = True
    if flag_spec or (not flag_num) or (not flag_lit):
        return ''
    return temp


def check_sumlock(temp) -> str:
    if temp == 'sumtolock':
        return temp
    return 'sumfromlock'


def check_mail(temp) -> str:
    if ('@' not in temp):
        return ''
    if (len(temp) > 40):
        return ''
    x = temp.split('@')
    if len(x) != 2:
        return ''
    if len(x[0]) < 1 or len(x[0]) > 35:
        return ''
    if len(x[1]) < 4:
        return ''
    if ('.' not in x[1]):
        return ''
    return temp


def check_wallet(temp):
    if (len(temp) > 50):
        return ''
    return temp


def check_wallet_add(temp):
    return temp
