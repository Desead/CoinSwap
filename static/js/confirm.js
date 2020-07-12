'use strict'
// проверить ситуацию с таймерами если страницу закрыли а потом открыли, к примеру уже после окончания таймера
// таймеры

let logo;
let pstype;
let screen_code;
let code_screen;
let swap_options;
let time_freeze;
let timerId;
let lastTime;

//вначале всегда читаем endpoint
let req = new XMLHttpRequest();
req.open('GET', '/api/');
req.send();


req.onload = function () {
    if (req.status !== 200) {
        console.log('Ошибка доступа')
        return
    }

    // let temp = document.querySelector('#cnf-status')
    // if (temp) {
    //     if (temp.innerText.indexOf('Новая') < 0) {
    //         document.querySelector('.solbtn').remove()
    //         document.querySelector('#cnf-cancel').remove()
    //         return
    //     }
    //
    // }


    logo = JSON.parse(req.response)['img']
    pstype = JSON.parse(req.response)['pstype']
    screen_code = JSON.parse(req.response)['screen_code']
    code_screen = JSON.parse(req.response)['code_screen']
    time_freeze = JSON.parse(req.response)['time_freeze']
    swap_options = JSON.parse(req.response)['swap_options']

    let temp = location.pathname.split('/')
    let left = temp[1]
    let right = temp[2]

    // если переводим с яндекса или с киви то на форме подтверждения включаем поле кошелёк с которого отдаём
    if ((left === 'QWRUB') || (left === 'YAMRUB')) {
        document.querySelector('#wallet_client_from').classList.remove('nodisplay');
    } else document.querySelector('#wallet_client_from').remove();


//устанавливаем таймер на ожидание перевода
    let timeescape = time_freeze[pstype[left]] * 60 * 1000;// переводим в миллисекунды время выделеное на ожидание оплаты
    timerId = setInterval(() => LastTimeToScreen(calcLastTime(getCreateDate(), getCurrentTime(), timeescape)), 100);
    setTimeout(() => changeCancel(timerId), timeescape);

    temp = document.getElementById('nobtn')
    temp.addEventListener('click', changeCancel);

    // если обмен ручной то нужна кнопка я оплатил и кошелёк куда перевести деньги
    // в авторежиме это не надо
    // в ступенчатых обменах часть может быть ручной а часть автоматической.

}


function calcLastTime(orderTimeCreate, currentTime, timeescape) {
    lastTime = Math.round((timeescape - (currentTime - orderTimeCreate)) / 1000)
    if (lastTime <= 0) cancelToScreen()
    return lastTime
}

function LastTimeToScreen(lt) {
    let temp = document.getElementById('cnf-cancel')
    if (temp)
        temp.innerText = 'До отмены заявки осталось: ' + Math.floor(lt / 60) + ' минут ' + lt % 60 + ' секунд';
}

function changeCancel(timerId) {
    clearInterval(timerId);
    // cancelToScreen();
}

// отменённую заявку можно обновить и тогда она вновь продолжить жить.
function cancelToScreen() {
    let temp = document.getElementById('cnf-status')
    if (temp) {
        temp.innerText = 'Статус заявки: Отменена'
        temp.style.color = 'red';
    }

    temp = document.getElementById('cnf-cancel')
    if (temp) temp.remove()

    temp = document.querySelectorAll('.sbtn')
    if (temp)
        for (let i of temp) {
            i.remove()
        }

    temp = document.querySelector('.wallet-manual')
    if (temp) temp.remove()

    if (timerId) clearInterval(timerId);
}


// всё время в UTC!
// получаем дату создания заявки из формы
function getCreateDate() {
    let temp = document.querySelector('#cnf-date').innerText
    temp = temp.split(': ')[1]
    temp = new Date(temp)
    return (+temp)
}

// получаем текущую дату
function getCurrentTime() {
    let temp = new Date()
    return +temp + temp.getTimezoneOffset() * 60000;
}


