from django.db import models
from django.utils.timezone import now
from src.additions.validators import validate_zero

# Список всех валют которые используются в работе обменника
class UsedMoneyModel(models.Model):
    usedmoney = models.CharField(max_length=10, unique=True, verbose_name='Название валюты', help_text='Валюты регистрозависимые. rub не равно RUB')
    description = models.CharField(max_length=255, verbose_name='Комментарий. Для себя.', blank=True)

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
    active_out = models.BooleanField(default=True,
                                     verbose_name='С платёжной системы можно оплачивать')  # Используется в обмене или нет
    screen = models.CharField(max_length=30, unique=True, verbose_name='Название для сайта')
    idbest = models.PositiveIntegerField(blank=True, unique=True, verbose_name='ID',
                                         null=True)  # ID платёжки на Bestchange'
    code = models.CharField(max_length=12, verbose_name='Код на бесте', unique=True)  # Код валюты на Bestchange
    # Название на Bestchange используем только для связи таблицы валют с сайта беста с парсингом беста где ID валют
    # name = models.CharField(max_length=30, verbose_name='Название', unique=True)
    moneytype = models.ForeignKey(MoneyTypeModel, on_delete=models.CASCADE, verbose_name='Тип')  # Тип платёжки
    usedmoney = models.ForeignKey(UsedMoneyModel, on_delete=models.SET_NULL,
                                  verbose_name='Базовая валюта платёжки',
                                  null=True)
    fee = models.FloatField(default=0,
                            verbose_name='Комиссия платёжной системы в %')  # плата за перевод в самой платёжке
    fee_fix = models.FloatField(default=0,
                                verbose_name='Фикс. комиссия платёжной системы')  # плата за перевод в самой платёжке
    fee_min = models.FloatField(default=0, verbose_name='мин комиссия')  # плата за перевод в самой платёжке
    fee_max = models.FloatField(default=0, verbose_name='макс комиссия')  # плата за перевод в самой платёжке
    reserve = models.FloatField(default=0, verbose_name='Текущий резерв')
    reserve_for_site = models.FloatField(default=0, verbose_name='Текущий резерв для сайта')
    max_balance = models.FloatField(default=0, verbose_name='Максимальный баланс платёжной системы')
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
    name = models.CharField(max_length=30, unique=True, verbose_name='Название сайта', default='localhost')
    url = models.URLField(unique=True, verbose_name='Адрес сайта', default='http://127.0.0.1:8000/')
    working = models.CharField(max_length=30, default='10:30 22:00', verbose_name='Время работы')
    mail = models.EmailField(default='info@change.ru', verbose_name='Почта для связи', blank=True)
    news = models.TextField(default='', blank=True, verbose_name='Новость на главную')
    first_num = models.PositiveIntegerField(default=0, verbose_name='Номер первой заявки', validators=[validate_zero])
    technical_work = models.BooleanField(default=False, verbose_name='Технические работы')
    description = models.CharField(max_length=255, blank=True, verbose_name='Комментарий. Для себя')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Сайт'
        verbose_name_plural = '1. Сайты'
        ordering = ['name']


# Общие настройки обменника.
# class ExchangeSettings(models.Model):
#     site = models.ForeignKey(SiteModel, on_delete=models.CASCADE, verbose_name='Настройки для сайта',
#                              default=0)
#
#     first_num22 = models.PositiveIntegerField(default=0, verbose_name='Номер первой заявки', validators=[validate_zero])
#     news = models.TextField(default='', verbose_name='Текст новости на главной')
#     technical_work = models.BooleanField(default=False, verbose_name='Технические работы')
#     description = models.CharField(max_length=255, blank=True, verbose_name='Комментарий. Для себя')
#
#     def __str__(self):
#         return 'Настройки для ' + self.site.name
#
#     class Meta:
#         verbose_name = 'Настройки обменника'
#         verbose_name_plural = '5. Настройки обменника'


# Используемые города. Актуально для наличных обменов
class CityModel(models.Model):
    name = models.CharField(max_length=100, default='')
    description = models.CharField(max_length=255, blank=True, verbose_name='Комментарий. Для себя')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Город'
        verbose_name_plural = '5. Города'
        ordering = ['name']


# todo пока не решён впрос принадлежности кошельков сайтам. Всё используется везде или лучше дать доп.поле сайт?
# todo уникальность номера кошелька надо проверять внутри платёжки а не по всей базе кошельков
class WalletsModel(models.Model):
    pay = models.ForeignKey(PaySystemModel, on_delete=models.CASCADE, verbose_name='Платёжная система')
    name = models.CharField(max_length=90, unique=True, verbose_name='Название/номер/адрес')
    token = models.CharField(max_length=255, verbose_name='Токен/доп.поле кошелька', default=0)
    count_in = models.PositiveSmallIntegerField(default=0, verbose_name='Кол-во входов за сутки')
    count_out = models.PositiveSmallIntegerField(default=0, verbose_name='Кол-во выходов за сутки')
    money_in = models.FloatField(default=0, verbose_name='Денег пришло за сутки')
    money_in_rub = models.FloatField(default=0, verbose_name='Денег пришло за сутки в рублях')
    money_out = models.FloatField(default=0, verbose_name='Денег ушло за сутки')
    money_out_rub = models.FloatField(default=0, verbose_name='Денег ушло за сутки в рублях')
    max_balance = models.FloatField(default=0, verbose_name='Максимальный баланс кошелька')
    balance = models.FloatField(default=0, verbose_name='Текущий баланс кошелька')
    balance_rub = models.FloatField(default=0, verbose_name='Текущий баланс в рублях')
    reserv = models.FloatField(default=0, verbose_name='В резерве')
    max_trans = models.FloatField(default=0, verbose_name='Максимальная сумма разового пополнения')
    date = models.DateField(default=now, verbose_name='Дата смены доступов к кошельку')
    lock = models.BooleanField(default=False, verbose_name='Заблокирован')
    description = models.CharField(max_length=255, blank=True, verbose_name='Комментарий. Для себя')

    def __str__(self):
        return self.pay.screen + ': ' + self.name

    class Meta:
        verbose_name = 'Кошелёк'
        verbose_name_plural = 'Кошельки'
        ordering = ('pay', 'name')

