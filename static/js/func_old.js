'use strict'

function createLeft(firststart = true) {
    // куда добавлять
    let temp
    let whereAdd = document.querySelector('.left-change .change-dn')
    for (let i of changeside) {
        whereAdd.append(template_elem_change.content.cloneNode(true))
        temp = document.querySelector('.left-change .change-dn .elem.toside')
        temp.classList.remove('toside')
        temp.classList.add('fromside')
        //добрались до логотипа. левый див платёжки
        temp.children[0].children[0].setAttribute('src', document.location.origin + '/' + logo[i[0]])
        //название платёжки. правый див платёжки
        temp.children[1].innerText = codescreen[i[0]]
    }
    //слева всегда одна платёжка должна быть выделена.
    if (firststart) {//если первый запуск то выбираем первую платёжку
        document.querySelector('.fromside').classList.add('seldiv')
    }
}

function createRight() {
    // console.log()
    // сначала смотрим какая платёжка выделена слева. отображать обмен нужно только для неё
    let left = document.querySelector('.fromside.seldiv .right').innerText
    //получаем код этой платёжки
    left = screencode[left]

    //ищем нашу платёжку
    for (let i of changeside) {
        if (left === i[0]) {// нашли нашу платёжку
            let whereAdd = document.querySelector('.right-change .change-dn')
            for (let j = 1; j < i.length; j++) {
                whereAdd.append(template_elem_change.content.cloneNode(true))
            }
            // теперь пробежимся по всем платёжкам справа и присвоим им нужные свойства. С правой сторонй удобнее сначала их все
            // добавить а потом перебрать в отличие от левой, где можно было делать это сразу
            let right = document.querySelectorAll('.toside')
            let count = 1;
            for (let j of right) {
                //добрались до логотипа. левый див платёжки
                j.children[0].children[0].setAttribute('src', document.location.origin + '/' + logo[i[count][0]])
                //название платёжки. правый див платёжки
                j.children[1].innerText = codescreen[i[count][0]]
                if (!i[count][1]) {
                    j.classList.add('selectNone')
                }
                count++
            }
            break
        }
    }
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

        // вешеам событие редиректа если выбраны обе платёжки
        // let temp = document.querySelectorAll('.seldiv')
        // if (temp.length === 2) {
        //     let left, right;
        //     for (let i of temp) {
        //         if (i.classList.contains('fromside')) {
        //             left = i.children[1].innerText
        //             left = screencode[left]
        //         }
        //         if (i.classList.contains('toside')) {
        //             right = i.children[1].innerText
        //             right = screencode[right]
        //         }
        //     }
        //     // window.location.href = '/' + left + '/' + right + '/';
        // }
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

let lft = 0
let rgt = 0

//узнаём сколько цифр после запятой в числе. На вход получаем строку
function inDigits(num) {
    let pos = num.indexOf('.')
    if (pos !== -1) {
        return num.length - pos - 1
    }
    return 0
}

// корректируем форму для ввода данных на обмен в зависимости от выбранных платёжек
function correctForm() {
    let left = document.querySelector('.fromside.seldiv').innerText
    let right = document.querySelector('.toside.seldiv').innerText

    // получаем лимиты для переводов
    document.querySelector('.from>.line1').innerText = "Отдаём " + left;
    document.querySelector('.to>.line1').innerText = "Получаем " + right;
    let name = left + right
    document.querySelector('#minfrom').innerText = "мин: " + stat[name + "minfrom"]
    document.querySelector('#maxfrom').innerText = "макс: " + stat[name + "maxfrom"]
    document.querySelector('#minto').innerText = "мин: " + stat[name + "minto"]
    document.querySelector('#maxto').innerText = "макс: " + stat[name + "maxto"]
    document.querySelector('#reservto').innerText = "резерв: " + stat[name + "reservto"]

    // удаляем ненужные поля

    // при отдаче клиентом с киви или яндекса нужно указать сумму и кошелёк откдуа мерчант снимет деньги. Для всех остальных
    // платёжек достаточно одного поля - сумма
    let temp;
    if (left.toUpperCase().includes('QIWI')) {
        temp = document.querySelector('#walletfrom')
        temp.placeholder = 'номер кошелька Qiwi: +79112345678'
        walletfrom.addEventListener('blur', checkQiwi)


    } else if (left.toUpperCase().includes('YANDEX') || left.toUpperCase().includes('ЯНДЕКС')) {
        temp = document.querySelector('#walletfrom')
        temp.placeholder = 'номер кошелька: 10-16 цифр'
        walletfrom.addEventListener('blur', checkYa)
    } else document.querySelector('.line3').remove();

    // корректируем поля для раздела - клиент получает.
    switch (pstype[right]) {
        case 'cash':
            break
        case 'moneysend':
            break
        case 'bank':
            temp = document.querySelector('#walletto')
            temp.placeholder = 'Введите номер карты'
            temp.addEventListener('blur', checkCard)
            break
        case 'code':
            break
        case 'eps':
            if (right.toUpperCase().includes('QIWI')) {
                temp = document.querySelector('#walletto')
                temp.placeholder = 'номер кошелька Qiwi: +79112345678'
                temp.addEventListener('blur', checkQiwi)
            } else if (right.toUpperCase().includes('YANDEX') || right.toUpperCase().includes('ЯНДЕКС')) {
                temp = document.querySelector('#walletto')
                temp.placeholder = 'номер кошелька: 10-16 цифр'
                temp.addEventListener('blur', checkYa)
            } else if (right.toUpperCase().includes('ADVANCED')) {
                temp = document.querySelector('#walletto')
                temp.placeholder = 'кошелёк Advanced Cash'
            } else if (right.toUpperCase().includes('PERFECT')) {
                temp = document.querySelector('#walletto')
                temp.placeholder = 'номер аккаунта Perfect Money'
            }

            break
        case 'crypto':
            temp = document.querySelector('#comiss')
            temp.classList.remove('nodisplay')
            temp = document.querySelector('#walletto')
            temp.placeholder = 'адрес ' + right;
            switch (right) {
                case 'Ripple (XRP)':
                    temp = document.querySelector('#walletadddata')
                    temp.placeholder = 'тег назначения Ripple'
                    temp = document.querySelector('#walletadd')
                    temp.classList.remove('nodisplay')
                    break
                case 'EOS (EOS)':
                    temp.placeholder = 'аккаунт EOS';
                    temp = document.querySelector('#walletadddata')
                    temp.placeholder = 'Memo'
                    temp = document.querySelector('#walletadd')
                    temp.classList.remove('nodisplay')
                    break
            }
            break
    }

    //Вешаем события на суммы ввода
    document.querySelector('#sumfrom').addEventListener('input', getRates)
    document.querySelector('#sumto').addEventListener('input', getRates)
    document.querySelector('#sumfrom').addEventListener('blur', lf)
    document.querySelector('#sumto').addEventListener('blur', rf)
    document.querySelector('#minfrom').addEventListener('click', minfr)

    //вешаем проверу на номер телефона
    document.querySelector('#phone').addEventListener('blur', checkQiwi)

    //Пишем курс обмена для ознакомления. он здесь округлён до 3 знака
    let kffrom = stat[left + right + 'from']
    let kfto = stat[left + right + 'to']
    let min = Math.min(kffrom, kfto)
    kffrom = (kffrom / min).toFixed(3)
    kfto = (kfto / min).toFixed(3)

    chrates.innerText = 'Обмен ' + kffrom + ' : ' + kfto
}

//проверяем корректность ввода
function lf() {
    this.value = lft
}

function rf() {
    this.value = rgt
}

//Поулчаем курсы обмена
//вешаем на событие клик, а если человек табом перемещается по сайту ,что тогда ?
function getRates() {
    let outstr = str2num(this.value)

    let left = document.querySelector('.fromside.seldiv').innerText
    let right = document.querySelector('.toside.seldiv').innerText

    let tpfrom = pstype[left]
    let tpto = pstype[right]

    let dgfrom = 2
    let dgto = 2
    if (tpfrom === 'crypto') dgfrom = 8
    if (tpto === 'crypto') dgto = 8

    let kffrom = stat[left + right + 'from']
    let kfto = stat[left + right + 'to']

    switch (this.id) {
        case 'sumfrom':
            // присваиваем минимальное значение чтобы не добавлять ненужные нули
            dgfrom = Math.min(dgfrom, inDigits(String(outstr)))
            lft = outstr.toFixed(dgfrom)
            rgt = (lft * kfto) / kffrom
            rgt = rgt.toFixed(dgto)
            sumto.value = rgt
            break
        case 'sumto':
            dgto = Math.min(dgto, inDigits(String(outstr)))
            rgt = outstr.toFixed(dgto)
            lft = (rgt * kffrom) / kfto
            lft = lft.toFixed(dgfrom)
            sumfrom.value = lft
            break
    }
}

//убираем из строки ввода все буквы, запятую преобразуем в точку и разрешаем только одну точку
function str2num(temp) {
    let res = []
    let coma = false;
    for (let i of temp) {
        if (i === '.' || i === ',') {
            if (coma) continue;
            res.push('.');
            coma = true;
        } else if (i === '0') res.push(i);
        else if (+i) res.push(i);
    }
    let outstr = '';
    for (let i of res) outstr += i
    return +outstr;
}

//обработка нажатия на мин и макс
function minfr() {
    // sumfrom.value = minfrom.innerText.slice(5)
    // если вызвать здесь функции getRates, lf,rf то возникает проблема с this.Надо эту ситуацию предсмотреть
}