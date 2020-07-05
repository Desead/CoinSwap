'use strict'

// при вводе мин и максимум через клик надо повесить события на соответствуюие расчёты курса и всё остальное
// дополнительная комиссия может меняться в зависимости от сумм обмена. надо это учесть, сейчас не считается

function createLeft() {
    let mx = sort2elem(sort_from)
    let temp
    let whereAdd = document.querySelector('.left-change .change-dn')
    for (let i of mx) {
        whereAdd.append(template_elem_change.content.cloneNode(true))
        temp = document.querySelector('.left-change .change-dn .elem.toside')
        temp.classList.remove('toside')
        temp.classList.add('fromside')

        //добрались до логотипа. левый див платёжки
        createLogo(temp, i[1])

        //название платёжки. правый див платёжки
        temp.children[1].innerText = code_screen[i[1]]
    }
    //слева всегда одна платёжка должна быть выделена.
    temp = document.querySelector('.fromside')
    if (temp) temp.classList.add('seldiv')
}

function createRight() {
    let mx = sort2elem(sort_to)
    // сначала смотрим какая платёжка выделена слева. отображать обмен нужно только для неё
    let left = document.querySelector('.fromside.seldiv .right')
    if (left)
        left = left.innerText;
    else return
    //получаем код этой платёжки
    left = screen_code[left]

    //ищем нашу платёжку
    for (let i in swap) {
        if (left === i) {// нашли нашу платёжку

            // добавили пустой элемент
            let whereAdd = document.querySelector('.right-change .change-dn')
            for (let j in swap[i]) {
                whereAdd.append(template_elem_change.content.cloneNode(true))
            }
            // теперь пробежимся по всем платёжкам справа и присвоим им нужные свойства. С правой сторонй удобнее сначала их все
            // добавить а потом перебрать в отличие от левой, где можно было делать это сразу
            let right = document.querySelectorAll('.toside')
            let count = 0;
            // перебираем общий отсортированный массив справа и ищем те платёжки которые используются у нас.
            // Таким образом выведем сразу всё отсортированное
            for (let j of mx) {
                if (swap[i].indexOf(j[1]) >= 0) {
                    right[count].children[1].innerText = code_screen[j[1]]
                    // right[count].id = j[1]+'_to'
                    createLogo(right[count], j[1])

                    // делаем через флаг потому что возможны ступенчатые курсы, где некоторые true а некоторые false
                    let flag = false
                    for (let k of swap_options[left + '_' + j[1]]) {
                        if (k.active) {
                            flag = true;
                            break;
                        }
                    }
                    if (!flag) right[count].classList.add('selectNone')
                    count++;
                }
            }
            break
        }
    }
}

// o = объект, psid ид этого объекта (платёжки)
// по уму бы сюда передать переменную static и тогда вообще проблем не будет с путями логотипа
function createLogo(o, psid) {
    if (logo[psid] === undefined)
        o.children[0].children[0].setAttribute('src', document.location.origin + '/static/img/' + psid + '.png')
    else
        o.children[0].children[0].setAttribute('src', document.location.origin + '/' + logo[psid])
}

// функция выделения платёжек
function psSelect() {

    // если выделена платёжка слева то везде слева удаляем класс выделения, а нажатой платёжке его добавляем
    if (this.classList.contains('fromside')) {
        let x = document.querySelectorAll('.fromside');
        for (let i = 0; i < x.length; i++)
            x[i].classList.remove('seldiv')
        this.classList.add('seldiv');
    }

    // если выделена платёжка справа то везде справа удаляем класс выделения, а нажатой платёжке его добавляем
    if (this.classList.contains('toside')) {
        let x = document.querySelectorAll('.toside');
        for (let i = 0; i < x.length; i++)
            x[i].classList.remove('seldiv')
        this.classList.add('seldiv');

        //удаляем блок новостей так как выделено 2 платёжки
        let temp = document.querySelector('.swap.block');
        if (temp) temp.remove();

        // блок для ввода данных обмена/ сначала удалим старый если есть
        temp = document.querySelector('.money')
        if (temp) temp.remove();

        // добавляем блок для ввода данных обмена
        temp = document.querySelector('.change')
        temp.append(template_change.content.cloneNode(true))

        correctForm();
    }
}

// меняем платёжки справа в зависимости от того что выделено слева
function changeRight() {
    let temp = document.querySelectorAll('.toside')
    for (let i of temp) {
        i.remove();
    }
    createRight()
    //если платёжки удаляли значит надо вновь повесить событие на переключение для правых платёжек
    temp = document.querySelectorAll('.toside')
    for (let i of temp) {
        if (!i.classList.contains('selectNone'))
            i.addEventListener('click', psSelect)
    }
}

// корректируем форму для ввода данных на обмен в зависимости от выбранных платёжек
function correctForm() {
    let temp;
    let left = screen_code[document.querySelector('.fromside.seldiv').innerText]
    let right = screen_code[document.querySelector('.toside.seldiv').innerText]
    let right_type = pstype[right]
    let left_type = pstype[left]

    //включаем или отклчаем иконку телефон около поля ввода телефона если есть перевод с\на киви.
    if (left.indexOf('QW') === 0 || right.indexOf('QW') === 0) {
        temp = document.querySelector('.triangle-left.nodisplay')
        temp.classList.remove('nodisplay')
        temp.addEventListener('click', Qiwi2Phone)
    }

    // меняем action в форме в зависимости от выбранных платёжек
    document.querySelector('#newAction').action = '/' + left + '/' + right + '/' + uuidv4() + '/'

    //изменяем в блоке название отдаваемой и получаемой валюты
    document.querySelector('.from .line1').innerText = 'Отдаю: ' + code_screen[left]
    document.querySelector('.to .line1').innerText = 'Получаю: ' + code_screen[right]

    // получаем лимиты для переводов. перебираем все значения в цикле из-за ступенчатых курсов
    let change_name = swap_options[left + '_' + right]

    let temp_from = 9999999999;
    let temp_to = 9999999999;
    for (let i in change_name) {
        if (!change_name[i].active) continue;
        temp_from = Math.min(temp_from, change_name[i].pay_from_min)
        temp_to = Math.min(temp_to, change_name[i].pay_to_min)
    }
    document.querySelector('#minfrom').innerText = "мин: " + temp_from
    document.querySelector('#minto').innerText = "мин: " + temp_to

    temp_from = 0;
    temp_to = 0;
    for (let i in change_name) {
        if (!change_name[i].active) continue;
        temp_from = Math.max(temp_from, change_name[i].pay_from_max)
        temp_to = Math.min(Math.max(temp_to, change_name[i].pay_to_max), ps_fee_to[right].reserve)
    }
    document.querySelector('#maxfrom').innerText = "макс: " + temp_from
    document.querySelector('#maxto').innerText = "макс: " + temp_to

    document.querySelector('#reservto').innerText = "резерв: " + ps_fee_to[right].reserve

    // корректируем верх формы. зависит от платёжек слева
    if (left.includes('QW')) {//если это какое то киви
        temp = document.querySelector('#wallet_client_from')
        temp.placeholder = 'номер кошелька Qiwi: 79112345678'
        temp.addEventListener('input', str2numQiwiYandex)
    } else if (left === 'YAMRUB') {//если это яндекс
        temp = document.querySelector('#wallet_client_from')
        temp.placeholder = 'номер кошелька: 10-16 цифр'
        temp.addEventListener('input', str2numQiwiYandex)
    } else {
        temp = document.querySelector('.line3')
        if (temp) temp.remove();
    }


    // корректируем поля для раздела - клиент получает.
    if (right_type !== 'crypto') { // только в крипте возможно самому выбрать комиссию
        temp = document.querySelector('.line5')
        if (temp) temp.remove();
        temp = document.querySelector('.line6')
        if (temp) temp.remove();
    } else {
        temp = document.querySelector('.line6 .lock')
        temp.attributes.title.value = 'Используется рекомендуемая нодой комиссия. Если не устраивает, введите свою. Комиссия полностью оплачивается клиентом'
    }


    switch (right_type) {
        case 'cash':
            break
        case 'moneysend':
            break
        case 'bank':
            temp = document.querySelector('#wallet_client_to')
            temp.placeholder = 'Введите номер карты:  10-19 цифр'
            temp.addEventListener('input', str2numCardOrPhone)
            break
        case 'code':
            break
        case 'eps':
            temp = document.querySelector('#wallet_client_to')
            if (right.indexOf('QW') === 0) {
                temp.placeholder = 'номер кошелька Qiwi: 79112345678'
                temp.addEventListener('input', str2numQiwiYandex)
            } else if (right === 'YAMRUB') {
                temp.placeholder = 'номер кошелька: 10-16 цифр'
                temp.addEventListener('input', str2numQiwiYandex)
            } else if (right === 'ADVC') {
                temp.placeholder = 'кошелёк Advanced Cash'
            } else if (right === 'PMUSD') {

            } else if (right === 'PMEUR') {

            } else if (right === 'PMBTC') {

            }
            break
        case 'crypto':
            document.querySelector('#wallet_client_to').placeholder = 'Адрес ' + code_screen[right]
            document.querySelector('#fee_client').addEventListener('input', str2num)
            document.querySelector('#fee_client').addEventListener('blur', reCalc)
            if (right === 'XRP') {
                document.querySelector('#wallet_add').placeholder = 'тег назначения Ripple'
            } else if (right === 'EOS') {
                document.querySelector('#wallet_client_to').placeholder = 'аккаунт ' + code_screen[right]
                document.querySelector('#wallet_add').placeholder = 'Memo'
            } else {
                temp = document.querySelector('.line5')
                if (temp) temp.remove();
            }
            break
    }

    // проверка ввода суммы и почты
    document.querySelector('#sum_from').addEventListener('input', str2num)
    document.querySelector('.btn').addEventListener('click', checkForm)
    document.querySelector('#sum_to').addEventListener('input', str2num)
    document.querySelector('.mailfree').addEventListener('click', mailFree)
    document.querySelector('#phone').addEventListener('input', str2numCardOrPhone)
    document.querySelector('#phone').addEventListener('blur', minPhone)
    temp = document.querySelector('#myfee')
    if (temp) temp.addEventListener('click', clearFee)

    // сразу рассчитываем курс обмена
    document.querySelector('#sum_from').addEventListener('input', rates)
    document.querySelector('#sum_to').addEventListener('input', rates)

    // вешаем событие ввода мин и макс в соответствующие поля через клик
    temp = document.querySelectorAll('.minmaxfrom')
    for (let i of temp) {
        i.addEventListener('click', exFrom)
    }
    temp = document.querySelectorAll('.minmaxto')
    for (let i of temp) {
        i.addEventListener('click', exTo)
    }
}


// все комиссии, прибыль, маржа и т.д. считаюстя всегда только с отдаваемой стороны
// если есть и фикс и % то сначала всегда считаем прцент потом фикс
// тут считаем все курсы обмена


function rates(side = 'test') {
    let left = screen_code[document.querySelector('.fromside.seldiv').innerText];
    let right = screen_code[document.querySelector('.toside.seldiv').innerText];

    let input_source = this;
    if (this === undefined)
        input_source = document.querySelector('#sum_from')
    let input_destination;
    input_destination = input_source.id === 'sum_from' ? document.querySelector('#sum_to') : document.querySelector('#sum_from');

    if (side === 'left') {
        input_source = document.querySelector('#sum_from')
        input_destination = document.querySelector('#sum_to')
    } else if (side === 'right') {
        input_source = document.querySelector('#sum_to')
        input_destination = document.querySelector('#sum_from')
    }

    let input_value = +input_source.value // сумма для обмена
    if (input_value <= 0) {
        document.querySelector('#sum_from').value = ''
        document.querySelector('#sum_to').value = ''
        return
    }
    let temp = 0;
    let prev = undefined;

    // смотрим есть ли своя комиссия
    let fee_client = document.querySelector('#fee_client')
    if (fee_client) {
        fee_client = Math.max(+fee_client.value, 0)
    } else fee_client = 0;

    // цикл нужен изза возможных ступенчатых курсов
    for (let i of swap_options[left + '_' + right]) {
        if (!i.active) continue;
        if (input_source.id === 'sum_from') {
            //сначала посчитали курс обмена, без комиссий.
            temp = +((input_value * (+i.rate_to) / (+i.rate_from)).toFixed(pstype[right] === 'crypto' ? 8 : 2))

            let fee = temp * (+i.fee) / 100 + i.fee_fix
            if (+i.fee_min > 0) fee = Math.max(fee, +i.fee_min)
            if (+i.fee_max > 0) fee = Math.min(fee, +i.fee_max)

            fee = +(fee.toFixed(pstype[right] === 'crypto' ? 8 : 2))

            temp = Math.max((temp - fee - fee_client), 0).toFixed(pstype[right] === 'crypto' ? 8 : 2)

            //выбираем лучший вариант для клиента
            if (prev === undefined) {
                prev = temp
                document.querySelector('#test_num').value = i.test_num
            } else {
                if (temp > prev) {
                    document.querySelector('#test_num').value = i.test_num
                    prev = temp;
                } else temp = prev;
            }

        } else if (input_source.id === 'sum_to') { // здесь нужно всё считать наоборот

            // Сначала нужно получить комиссию и сравнить её с минимальной
            // получили сумму от которой если отнять все комиссии то получим введённое значение
            temp = (input_value + (+i.fee_fix) + fee_client) * 100 / (100 - (+i.fee))
            // берём разницу чтобы получить комиссию
            temp = +((temp - input_value).toFixed(pstype[right] === 'crypto' ? 8 : 2))
            // сравниваем комиссию с минимальной
            temp = Math.max(temp, +i.fee_min)
            //поулчаем сумму из которой можно по курсу получить начальную величину обмена
            temp = temp + input_value
            // поулчаем начальную сумму обмена
            temp = +((temp * (+i.rate_from) / (+i.rate_to)).toFixed(pstype[left] === 'crypto' ? 8 : 2))

            if (prev === undefined) {
                prev = temp
                document.querySelector('#test_num').value = i.test_num
            } else {
                if (temp < prev) {
                    prev = temp;
                    document.querySelector('#test_num').value = i.test_num
                } else temp = prev;
            }

        }
    }

    input_destination.value = temp
}

//убираем из строки ввода все буквы, запятую преобразуем в точку и разрешаем только одну точку
function str2num() {
    // до скольки знаков округляем ввод. Сначала определим что именно мы округляем ,сумму селва ,справа или комиссию
    let rnd = 2;
    let max_input = 0;

    if (this.name === 'sum_from') {
        if (pstype[screen_code[document.querySelector('.fromside.seldiv').innerText]] === 'crypto') rnd = 8;
        max_input = +document.querySelector('#maxfrom').innerText.split(': ')[1];
    } else if (this.name === 'sum_to') {
        if (pstype[screen_code[document.querySelector('.toside.seldiv').innerText]] === 'crypto') rnd = 8;
        max_input = +document.querySelector('#maxto').innerText.split(': ')[1];
    } else {
        rnd = 8;//значит мы в поле с доп.комиссией
        max_input = +document.querySelector('#maxto').innerText.split(': ')[1];
    }
    let res = []
    let coma = false;
    for (let i of this.value) {
        if (i === '.' || i === ',') {
            if (coma) continue;
            res.push('.');
            coma = true;
        } else if (i === '0' && rnd > 0) {
            res.push(i);
            if (coma) rnd--;
        } else if (+i && rnd > 0) {
            res.push(i);
            if (coma) rnd--;
        }
    }

    this.value = res.join('');
}


function str2numQiwiYandex() {
    let res = []
    let temp = 16;
    for (let i of this.value) {
        if (i === '0') {
            if (temp > 0) res.push(i);
            temp--;
        } else if (+i) {
            if (temp > 0) res.push(i);
            temp--;
        }
    }
    this.value = res.join('');
}

function str2numCardOrPhone() {
    let res = []
    let temp = 19;
    for (let i of this.value) {
        if (i === '0') {
            if (temp > 0) res.push(i);
            temp--;
        } else if (+i) {
            if (temp > 0) res.push(i);
            temp--;
        }
    }
    this.value = res.join('');
}

function Qiwi2Phone() {
    let temp = document.querySelector('#wallet_client_from')
    if (!temp) temp = document.querySelector('#wallet_client_to')
    temp = temp.value
    if (temp.length >= 11)
        document.querySelector('#phone').value = temp
}

function mailFree() {
    document.querySelector('#mail').value = 'fake@mail.ru'
}

// телефон должен быть более 10 символов
function minPhone() {
    let temp = this.value;
    if (temp.length < 11) this.value = ''
}

function uuidv4() {
    return 'xxxxxxxx_xxxx_4xxx_yxxx_xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
        var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}

// вставляем мин и макс в инпуты
function exFrom() {
    document.querySelector('#sum_from').value = this.innerText.split(': ')[1];
    rates('left');
}

function exTo() {
    document.querySelector('#sum_to').value = this.innerText.split(': ')[1];
    rates('right');
}

// сортировка матрицы по второму столбцу. Создаём js матрицу - массив массивов и её уже сортируем
function sort2elem(mx) {
    let temp = [];
    for (let i in mx) {
        temp.push([mx[i], i])
    }
    return temp.sort()
}

// пересчитываем изза изменения пользовательской комиссии
function reCalc() {
    let temp = document.querySelector('#sum_from')
    if (temp)
        if (temp.value > 0) {
            temp = document.querySelector('#sum_to')
            if (temp)
                if (temp.value > 0) {
                    temp = document.getElementsByName('sumlock')
                    if (temp)
                        for (let i of temp)
                            if (i.checked) {
                                if (i.value === 'sumfromlock') rates('left')
                                else rates('right')
                                return
                            }
                    rates('left')
                }
        }
}

// если ничего не изменилось то и нет смысла пересчитывать. нереализовано
function clearFee() {
    let temp = document.getElementsByName('sumlock')

    if (temp)
        for (let i of temp)
            if (i.checked) {
                document.querySelector('#fee_client').value = '';
                if (i.value === 'sumtolock') rates('right')
                else rates('left')
                break;
            }
}

// проверяем корректность ввода в форме
function checkForm() {
    // очищаем все варнинги и если надо то ставим новые
    let temp = document.querySelectorAll('.warning')
    for (let i of temp) {
        i.classList.remove('warning')
    }

    let input_check = +document.querySelector('#sum_from').value
    let max_check = +document.querySelector('#maxfrom').innerText.split(': ')[1];
    let min_check = +document.querySelector('#minfrom').innerText.split(': ')[1];


    if (input_check < min_check) {
        document.querySelector('#minfrom').classList.add('warning')
        document.querySelector('#sum_from').classList.add('warning')
    }

    if (input_check > max_check) {
        document.querySelector('#maxfrom').classList.add('warning')
        document.querySelector('#sum_from').classList.add('warning')
    }

    input_check = +document.querySelector('#sum_to').value
    max_check = +document.querySelector('#maxto').innerText.split(': ')[1];
    min_check = +document.querySelector('#minto').innerText.split(': ')[1];

    if (input_check < min_check) {
        document.querySelector('#minto').classList.add('warning')
        document.querySelector('#sum_to').classList.add('warning')
    }

    if (input_check > max_check) {
        document.querySelector('#maxto').classList.add('warning')
        document.querySelector('#sum_to').classList.add('warning')
    }

    // если варнингов нету то разрешаем кнопке отправить форму
    if (document.querySelectorAll('.warning').length === 0) {
        document.querySelector('#newFormAction').attributes.type.value = 'submit';
    }
}

