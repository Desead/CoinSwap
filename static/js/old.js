
// Оставляем выделение и убираем его у остальных элементов. левые и правые части раздельно
function fa() {
    let left;
    let right;

    if (this.classList.contains('fromside')) {
        let x = document.querySelectorAll('.fromside');
        for (let i = 0; i < x.length; i++)
            x[i].classList.remove('seldiv')
        this.classList.add('seldiv');

        ViewRight(); //если выделили элемент слева, то обновляем часть справа
    }
    if (this.classList.contains('toside')) {
        let x = document.querySelectorAll('.toside');
        for (let i = 0; i < x.length; i++)
            x[i].classList.remove('seldiv')
        this.classList.add('seldiv');

        // если выделено 2 элемента то редиректим
        right = this.childNodes[1].innerText
        left = document.querySelector('.fromside.seldiv').childNodes[1].innerText
    }
    if (location.href === location.origin + '/')
        if (left !== undefined && right !== undefined)
            window.location.href = '/' + pscode[left] + '/' + pscode[right] + '/';

}


// подключаемся к endpoint и забираем данные в 2 глобальных объекта
function getApiData() {
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
        codescreen = JSON.parse(req.response)['codescreen']
        screencode = JSON.parse(req.response)['screencode']

        ViewLeft();
        ViewRight();
    }
}

// добавляем платёжки слева
function ViewLeft() {
    for (let i = 0; i < swap.length; i++) {
        addElements(swap[i][0], logo[swap[i][0]], true)
    }
    // выделяем первый элемент если справа выделения нету ещё
    if (location.href === location.origin + '/') {
        let temp = document.querySelector('.fromside');
        if (temp) temp.classList.add('seldiv');
    } else { // возвращаем выделение элемента слева после редиректа
        let left = location.pathname
        left = left.split('/')[1]
        let temp = document.querySelectorAll('.fromside')
        for (let i of temp) {
            if (pscode[i.childNodes[1].innerText] === left) {
                i.classList.add('seldiv');
                break
            }
        }
    }
}

// добавляем платёжки справа
function ViewRight() {
    // удаляем предыдущие элементы справа
    let node = document.querySelectorAll('.toside');
    for (let i = 0; i < node.length; i++) {
        node[i].remove();
    }

    // узнали какой элемент выделен слева
    let left = document.querySelector('.fromside.seldiv>.right')
    if (!left) return;
    left = left.innerText
    let right;

    for (let i = 0; i < swap.length; i++) {
        //получаем первый элемент справа. если равен слева значит это наш ряд обмена
        right = swap[i][0]
        if (left === right) {
            for (let j = 1; j < swap[i].length; j++) {
                addElements(swap[i][j], logo[swap[i][j]], false)
            }
            break;
        }
    }
    // если после редиректа то надо выделить элемент справа
    if (location.href !== location.origin + '/') {
        let right = location.pathname
        right = right.split('/')[2]

        let temp = document.querySelectorAll('.toside')
        for (let i of temp) {
            if (pscode[i.childNodes[1].innerText] === right) {
                i.classList.add('seldiv');
                removeNews();
                correctForm();
                break
            }
        }
    }
}

// когда выделена платёжка только с одной стороны то справа отображаем новостной блок
function removeNews() {
    // if (document.querySelectorAll('.seldiv').length === 2)
    {
        let temp = document.querySelector('.swap.block');
        if (temp) temp.remove();
        temp = document.querySelector('.swap.money');
        if (temp) temp.remove();
        temp = document.querySelector('.change')
        temp.append(tmpl.content.cloneNode(true));
    }
}


function removeNews() {
    let temp = document.querySelector('.swap.block');
    if (temp) temp.remove();
    // temp = document.querySelector('.swap.money');
    // if (temp) temp.remove();
    // temp = document.querySelector('.change')
    // temp.append(tmpl.content.cloneNode(true));

}

// создаём див платёжки
// psname - название платёжной системы
// logotip - путь к логотипу
// side - сторона добавления. true=слева, false=справа
function addElementsLeft(psname, logotip) {
    let change = document.createElement('div')
    change.className = 'elem fromside'

    // див платёжки состоит из 2х элементов
    // див слева - только логотип. див справа - название платёжки
    let left = document.createElement('div')
    left.className = 'left'

    let right = document.createElement('div')
    right.className = 'right'
    right.innerText = psname

    let pict = document.createElement('img')
    pict.height = 40
    pict.width = 40
    pict.src = document.location.origin + '/' + logotip

    let x = document.querySelector('.left-change .change-dn')
    x.append(change)
    change.addEventListener('click', fa);
    change.append(left)
    left.append(pict)
    change.append(right)
}

// создаём див платёжки
// psname - название платёжной системы
// logotip - путь к логотипу
// side - сторона добавления. true=слева, false=справа
function addElements(psname, logotip, side) {
    console.log(side)
    let change = document.createElement('div')
    if (side) change.className = 'elem fromside'
    else change.className = 'elem toside'

    // див платёжки состоит из 2х элементов
    // див слева - только логотип. див справа - название платёжки
    let left = document.createElement('div')
    left.className = 'left'

    let right = document.createElement('div')
    right.className = 'right'
    right.innerText = psname

    let pict = document.createElement('img')
    pict.height = 40
    pict.width = 40
    pict.src = document.location.origin + '/' + logotip
    let x;
    if (side) x = document.querySelector('.left-change .change-dn')
    else x = document.querySelector('.right-change .change-dn')
    x.append(change)
    change.addEventListener('click', fa);
    change.append(left)
    left.append(pict)
    change.append(right)
}
