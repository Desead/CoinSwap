def str2float(temp: str) -> float:
    temp = temp.replace(',', '.')
    try:
        return float(temp)
    except:
        return 0


def str2int(temp: str) -> int:
    try:
        return int(temp)
    except:
        return 0


def check_pscode(temp) -> str:
    # проверка на длинну и на то что код состоит только из больших букв стоит в урл. Надо ли что то ещё ставить?
    return temp


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
    if (temp == 'sumfromlock') or (temp == 'sumtolock'):
        return temp
    else:
        return ''


def check_mail(temp) -> str:
    if ('@' not in temp):
        return ''
    if ('.' not in temp):
        return ''
    if (len(temp) > 30):
        return ''
    return temp


def check_wallet(temp):
    if (len(temp) > 50):
        return ''
    return temp


def check_wallet_add(temp):
    return temp
