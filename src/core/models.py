from django.db import models
from django.utils.timezone import now
from src.additions.validators import validate_more_zero, validate_zero


# Список всех валют которые используются в работе обменника
# todo так как считаем всё в рублях то валюты рубль в системе должна быть всегда
class UsedMoneyModel(models.Model):
    usedmoney = models.CharField(max_length=10, unique=True, verbose_name='Название валюты',
                                 help_text='Валюты регистрозависимые. rub не равно RUB')
    description = models.CharField(max_length=255, verbose_name='Комментарий. Для себя.', blank=True)

    def save(self, *args, **kwargs):
        self.usedmoney = self.usedmoney.upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.usedmoney

    class Meta:
        verbose_name = 'Валюта'
        verbose_name_plural = '2. Используемые валюты'
        ordering = ['usedmoney']


# типы платёжок и время ожидания перевода
class MoneyTypeModel(models.Model):
    moneytype = models.CharField(max_length=20, verbose_name='Тип платёжки')
    description = models.CharField(default='', max_length=100, verbose_name='Описание')
    freeze = models.PositiveSmallIntegerField(default=15, verbose_name='Время ожидания перевода в мин.')
    freeze_confirm = models.PositiveSmallIntegerField(default=0, verbose_name='Время ожидания подтверждения в мин.')

    def __str__(self):
        return self.description

    class Meta:
        verbose_name = 'Тип платёжной системы'
        verbose_name_plural = '3. Типы платёжных систем'


# Платёжная система. точнее платёжная система + валюта. К примеру не просто Webmoney а Webmoney MWZ
# а сама платёжка Webmoney выступает как мерчант. Так удобнее организовать внутреннюю структуру
# При добавлении платёжной системы, объязательно прописать её в js для фронта
# todo максимальный баланс надо считать сразу по всем кошелькам а не по одному
class PaySystemModel(models.Model):
    active = models.BooleanField(default=False, verbose_name='On/Off')  # Используется в обмене или нет
    active_out = models.BooleanField('С платёжной системы можно оплачивать', default=True)
    screen = models.CharField(max_length=30, unique=True, verbose_name='Название пс')
    idbest = models.PositiveIntegerField(blank=True, unique=True, verbose_name='ID', null=True)
    code = models.CharField(max_length=12, verbose_name='Код', unique=True)  # Символный код валюты на Bestchange
    moneytype = models.ForeignKey(MoneyTypeModel, on_delete=models.CASCADE, verbose_name='Тип')  # Тип платёжки
    usedmoney = models.ForeignKey(UsedMoneyModel, on_delete=models.SET_NULL, verbose_name='Базовая валюта', null=True)
    reserve = models.FloatField(default=0, verbose_name='Текущий резерв')
    reserve_for_site = models.FloatField(default=0, verbose_name='Резерв для сайта')
    max_balance = models.FloatField(default=0, verbose_name='Максимальный баланс')
    delay = models.PositiveIntegerField(default=0, verbose_name='Задержка перевода в сек')
    sort_from = models.PositiveSmallIntegerField(default=0, verbose_name='Место платёжной системы слева')
    sort_to = models.PositiveSmallIntegerField(default=0, verbose_name='Место платёжной системы справа')
    url = models.FileField(blank=True, verbose_name='Изображение', upload_to='static/img')
    description = models.TextField(blank=True, verbose_name='Комментарий. Для себя')

    def __str__(self):
        return self.screen

    class Meta:
        verbose_name = 'Платёжная система'
        verbose_name_plural = '4. Платёжные системы'
        # ordering = ['name']
        ordering = ['screen']


# используемые домены
class SiteModel(models.Model):
    technical_work = models.BooleanField('Технические работы', default=True)
    name = models.CharField('Название сайта', max_length=30, unique=True, default='localhost')
    url = models.URLField('Адрес сайта', unique=True, default='http://127.0.0.1:8000/')
    working = models.CharField('Время работы', max_length=30, default='10:30 22:00')
    mail = models.EmailField('Почта для связи', default='info@change.ru')
    first_num = models.PositiveIntegerField('Номер первой заявки', default=1000, validators=[validate_more_zero])
    news = models.TextField('Новость на главную', default='Новость на главной сайта')
    banner = models.TextField('Текст в баннер на главную', default='Сообщение в баннер')
    technical_text = models.TextField('Текст на сайт во время тех.работ', default='Ведутся технические работы')
    # confirm_text = models.TextField('Текст на страницу подтверждения для начала обмена', default='Подтвердите данные')
    description_text = models.TextField('Тэг страницы: description', default='Безопасный обмен денег')
    keywords_text = models.TextField('Тэг страницы: keywords', default='qiwi, btc, ltc, usd')
    title_text = models.TextField('Тэг страницы: title', default='Обменник')
    description = models.TextField('Комментарий. Для себя', max_length=255, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Сайт'
        verbose_name_plural = '1. Сайты'
        ordering = ['name']


# Используемые города. Актуально для наличных обменов
class CityModel(models.Model):
    name = models.CharField(max_length=100, default='')
    description = models.CharField(max_length=255, blank=True, verbose_name='Комментарий. Для себя')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Город'
        verbose_name_plural = '6. Города'
        ordering = ['name']


# todo пока не решён впрос принадлежности кошельков сайтам. Всё используется везде или лучше дать доп.поле сайт?
# todo уникальность номера кошелька надо проверять внутри платёжки а не по всей базе кошельков
class WalletsModel(models.Model):
    lock = models.BooleanField(default=False, verbose_name='Заблокирован')
    description = models.CharField(max_length=255, blank=True, verbose_name='Комментарий. Для себя')
    pay = models.ForeignKey(PaySystemModel, on_delete=models.CASCADE, verbose_name='Платёжная система')
    name = models.CharField(max_length=90, unique=True, verbose_name='Название/номер/адрес')
    token = models.CharField(max_length=255, verbose_name='Токен/доп.поле кошелька', default=0)
    count_in = models.PositiveSmallIntegerField(default=0, verbose_name='Кол-во входов за сутки')
    count_out = models.PositiveSmallIntegerField(default=0, verbose_name='Кол-во выходов за сутки')
    money_in = models.FloatField(default=0, verbose_name='Денег пришло за сутки')
    money_in_rub = models.FloatField(default=0, verbose_name='Денег пришло за сутки в рублях')
    money_out = models.FloatField(default=0, verbose_name='Денег ушло за сутки')
    money_out_rub = models.FloatField(default=0, verbose_name='Денег ушло за сутки в рублях')
    max_balance = models.FloatField(default=0, verbose_name='Максимальный баланс кошелька', validators=[validate_zero])
    balance = models.FloatField(default=0, verbose_name='Текущий баланс кошелька')
    balance_rub = models.FloatField(default=0, verbose_name='Текущий баланс в рублях')
    reserv = models.FloatField(default=0, verbose_name='В резерве', validators=[validate_zero])
    min_trans = models.FloatField(default=0, verbose_name='Минимальная сумма разового пополнения',
                                  validators=[validate_zero])
    max_trans = models.FloatField(default=0, verbose_name='Максимальная сумма разового пополнения',
                                  validators=[validate_zero])
    date = models.DateField(default=now, verbose_name='Дата смены доступов к кошельку')
    site = models.ManyToManyField(SiteModel, blank=True)

    def __str__(self):
        return self.pay.screen + ': ' + self.name

    class Meta:
        verbose_name = 'Кошелёк'
        verbose_name_plural = '5.Кошельки'
        ordering = ('pay', 'name')


# модель пользователя
class RegisteredUserModel(models.Model):
    user_site = models.ForeignKey(SiteModel, verbose_name='Сайт регистрации', on_delete=models.SET_NULL, null=True, blank=True)
    user_name = models.CharField('Имя', max_length=50, default='user name')
    user_mail = models.EmailField('Почта', default='user@user.ru')
    user_password = models.CharField('Пароль', max_length=50, default='user password')
    user_ip = models.CharField('IP пользователя', max_length=39, default='', blank=True)
    user_create = models.DateTimeField('Дата регистрации', default=now)
    user_discount = models.FloatField('Скидка пользователя', default=0)
    user_partner_id = models.PositiveIntegerField('Партнёрский ID', default=0, validators=[validate_zero])
    user_partner_link = models.URLField('Партнёрская ссылка', default='')
    user_partner_fee = models.FloatField('Партнёрский %', default='10', validators=[validate_zero])

    def __str__(self):
        return self.user_name

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
