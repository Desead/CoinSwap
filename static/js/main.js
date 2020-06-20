'use strict'

let logo;
let swap;
let stat;
let pstype;
let screencode;
let codescreen;
let changeside;

//вначале всегда читаем endpoint
let req = new XMLHttpRequest();
req.open('GET', '/api/');
req.send();

req.onload = function () {
    if (req.status !== 200) {
        console.log('Ошибка доступа')
        return
    }

    logo = JSON.parse(req.response)['img']
    swap = JSON.parse(req.response)['change']
    stat = JSON.parse(req.response)['stat']
    pstype = JSON.parse(req.response)['pstype']
    screencode = JSON.parse(req.response)['screencode']
    codescreen = JSON.parse(req.response)['codescreen']
    changeside = JSON.parse(req.response)['changeside']

    // если это первый запуск то создаём платёжки слева и справа
    if (location.href === location.origin + '/') {
        createLeft()
        createRight()

        //вешаем события переключение платёжек слева и справа
        let temp = document.querySelectorAll('.elem')
        for (let i of temp) {
            if (!i.classList.contains('selectNone'))
                i.addEventListener('click', psSelect)
        }
        //вешаем события изменение платёжек справа в зависимости от выбранной слева
        temp = document.querySelectorAll('.fromside')
        for (let i of temp) {
            i.addEventListener('click', changeRight)
        }

        //отображаем новостной блок
        temp = document.querySelector('.swap')
        temp.append(template_news_block.content.cloneNode(true))
        document.querySelector('.swap .change-up').innerText = 'Новости'

    }
    // else {// сюда приходим после редиректа
    //     //главная страница, но уже выбраны для обмена обе платёжки
    //     //в этом случае адресная стркоа состоит из 4 элементов: ['','ps1','ps2','']
    //     if (location.pathname.split('/').length === 4) {
    //         createLeft(false)
    //
    //         // узнаём что было выделено до этого
    //         let left, right, temp = location.pathname.split('/')
    //         left = codescreen[temp[1]]
    //         right = codescreen[temp[2]]
    //
    //         //выделяем слева туже платёжку
    //         temp = document.querySelectorAll('.fromside')
    //         for (let i of temp) {
    //             if (i.children[1].innerText === left) {
    //                 i.classList.add('seldiv')
    //                 break
    //             }
    //         }
    //
    //         // отображаем правые платёжки
    //         createRight();
    //
    //         //выделяем справа туже платёжку
    //         temp = document.querySelectorAll('.toside')
    //         for (let i of temp) {
    //             if (i.children[1].innerText === right) {
    //                 i.classList.add('seldiv')
    //                 break
    //             }
    //         }
    //
    //         //вешаем события переключение платёжек слева и справа
    //         temp = document.querySelectorAll('.elem')
    //         for (let i of temp) {
    //             if (!i.classList.contains('selectNone'))
    //                 i.addEventListener('click', psSelect);
    //         }
    //         //вешаем события изменение платёжек справа в зависимости от выбранной слева
    //         temp = document.querySelectorAll('.fromside')
    //         for (let i of temp) {
    //             i.addEventListener('click', changeRight)
    //         }
    //
    //         //удаляем блок новостей
    //         temp = document.querySelector('.swap.block');
    //         if (temp) temp.remove();
    //
    //         // добавляем блок для ввода данных обмена
    //         temp = document.querySelector('.change')
    //         temp.append(template_change.content.cloneNode(true))
    //
    //         // обновляем блок обмена в зависимости от выбранных платёжек
    //         correctForm();
    //     } else {//страница подтверждения выглядит так: : ['','ps1','ps2','confirm','']
    //
    //         let temp = location.pathname.split('/')
    //         let left = temp[1]//платёжка слева
    //         let right = temp[2]//платёжка справа
    //
    //         // изменили валюту отдачи и получения
    //         document.querySelector('#cnf-from').innerText = 'Отдаёте: ' + codescreen[left]
    //         document.querySelector('#cnf-to').innerText = 'Получаете: ' + codescreen[right]
    //
    //         //устанавливаем таймер на ожидание перевода
    //         let timeescape = 900000;// 15 минут в секундах = 15*60*1000 = 900000
    //         let now = Date.now()
    //         let timerId = setInterval(() => changeTimer(now, timeescape), 1000);
    //
    //         // document.querySelector('#cnf-freeze').innerText = 'Период заморозки курса: ' + Math.floor(timeescape / 1000 / 60) + ' минут'
    //         document.querySelector('#cnf-cancel').innerText = 'До отмены заявки осталось: ' + Math.floor(timeescape / 1000 / 60) + ' минут'
    //
    //         // Добавим дату и время оформления
    //         let dt = new Date()
    //         dt = dt.toUTCString()
    //         dt = dt.split(',')[1].trim()
    //         dt = dt.split(' ')
    //         document.querySelector('#cnf-date').innerText = 'Дата оформления: ' + dt[0] + ' ' + dt[1] + ' ' + dt[2]
    //         document.querySelector('#cnf-time').innerText = 'Время оформления (UTC): ' + dt[3]
    //
    //
    //         //тормозим через 15 минут. 15*60*1000
    //         setTimeout(() => changeCancel(timerId), timeescape);
    //
    //         temp = document.getElementById('nobtn')
    //         temp.addEventListener('click', changeCancel);
    //     }
    // }// сюда приходим после редиректа
}



