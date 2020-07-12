'use strict'

let temp = document.querySelector('.active')
if (temp)
    temp.classList.remove('active')

temp = document.querySelector('#index_page')
if (temp)
    temp.classList.add('active')

let logo;
let pstype;
let screen_code;
let code_screen;
let swap;
let swap_options;
let sort_from;
let sort_to;
let ps_fee_to;

// let left_money_type;
// let right_money_type;

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
    pstype = JSON.parse(req.response)['pstype']
    screen_code = JSON.parse(req.response)['screen_code']
    code_screen = JSON.parse(req.response)['code_screen']
    swap = JSON.parse(req.response)['swap']
    swap_options = JSON.parse(req.response)['swap_options']
    sort_from = JSON.parse(req.response)['sort_from']
    sort_to = JSON.parse(req.response)['sort_to']
    ps_fee_to = JSON.parse(req.response)['ps_fee_to']

    // создали первоначальынй вид платёжек
    createLeft();
    createRight();

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
}
