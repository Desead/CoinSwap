from django.db import models
from django.utils.timezone import now
from src.core.models import PaySystemModel, SiteModel, UsedMoneyModel, CityModel, RegisteredUserModel
from src.parsers.models import AllRates
from django.contrib.auth.models import User
from src.additions.validators import validate_zero, validate_more_zero


class OrderModel(models.Model):
    STATUS_CHOISES = (
        ('ok', 'Выполнена'),
        ('new', 'Новая заявка'),
        ('cancel', 'Отменена'),
        ('error', 'Ошибка'),
    )
    LOCK_CHOISES = (
        ('from', 'Отдаваемая сумма'),
        ('to', 'Принимаемая сумма'),
    )
    num = models.PositiveIntegerField(auto_created=True, verbose_name='Номер заявки', default=1000, editable=False)
    numuuid = models.CharField('UUID', max_length=36, editable=False)
    site = models.ForeignKey(SiteModel, on_delete=models.CASCADE, verbose_name='Сайт', null=True, default=0)
    status = models.CharField(max_length=50, choices=STATUS_CHOISES, default='new', verbose_name='Статус заявки')
    data_create = models.DateTimeField(default=now, verbose_name='Дата создания заявки', editable=False)
    data_change = models.DateTimeField(default=now, verbose_name='Дата изменения заявки')
    pay_from = models.ForeignKey(PaySystemModel, on_delete=models.CASCADE, verbose_name='Клиент отдаёт пс',
                                 related_name='pay_from_order')
    pay_to = models.ForeignKey(PaySystemModel, on_delete=models.CASCADE, verbose_name='Клиент получает пс',
                               related_name='pay_to_order')
    sum_from = models.FloatField(default=0, verbose_name='Клиент отдаёт')
    sum_from_rub = models.FloatField(default=0, verbose_name='Сколько отдаёт в рублях')
    sum_to = models.FloatField(default=0, verbose_name='Клиент получает')
    sum_to_rub = models.FloatField(default=0, verbose_name='Клиент получает в рублях')
    partner = models.FloatField(default=0, verbose_name='Прибыль партнёра')
    partner_rub = models.FloatField(default=0, verbose_name='Прибыль партнёра в рублях')
    profit = models.FloatField('Наша прибыль', default=0, help_text='В прибыли присутствует комиссия за перевод')
    profit_rub = models.FloatField('Наша прибыль в рублях', default=0,
                                   help_text='В прибыли присутствует комиссия за перевод')
    lock = models.CharField(max_length=50, choices=LOCK_CHOISES, default='from', verbose_name='Неизменная сумма')
    rate = models.CharField(max_length=255, default=0, verbose_name='Курс обмена')
    rate_best = models.CharField(max_length=255, default=0, verbose_name='Курс на бесте')
    rate_cb = models.CharField(max_length=255, default=0, verbose_name='Биржевой курс')
    fee = models.FloatField(default=0, verbose_name='Комиссия сделки')
    fee_client = models.FloatField(default=0, verbose_name='Пользовательская комиссия')
    # движение денег: wallet_client_from -> wallet_exchange_to; wallet_exchange_from -> wallet_client_to
    wallet_client_from = models.CharField(max_length=16, verbose_name='Кошелёк c которого клиент отдаёт', blank=True)
    wallet_client_to = models.CharField(max_length=50, verbose_name='Кошелёк на который клиент получает')
    wallet_exchange_from = models.CharField('Кошелёк с которого обменник отдаёт', max_length=50, default='')
    wallet_exchange_to = models.CharField('Кошелёк на который обменник получает', max_length=50, default='')
    wallet_add = models.CharField(max_length=50, verbose_name='Доп.поле для крипты', blank=True)
    # client = models.ForeignKey(RegisteredUserModel, on_delete=models.SET_NULL, null=True, blank=True, default='')
    confirm_text = models.TextField('Текст на страницу подтверждения для начала обмена', default='Подтвердите данные')
    description_text = models.TextField('Тэг страницы: description', default='Безопасный обмен денег')
    keywords_text = models.TextField('Тэг страницы: keywords', default='qiwi, btc, ltc, usd')
    title_text = models.TextField('Тэг страницы: title', default='Обменник')
    description = models.TextField(blank=True, verbose_name='Комментарий. Для себя')
    url_change = models.URLField('Ссылка на заявку', default='')

    def __str__(self):
        return str(self.num) + ': ' + self.pay_from.screen + ' -> ' + self.pay_to.screen

    class Meta:
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки на обмен'
        ordering = ['-num']


# todo нужна проверка чтобы нельзя было создавать дво одинаковых направления обмена
# todo в заявку надо сохранять слепок всех участвующих в обмене цифр, тогда можно будет решить все проблемы
class ChangeModel(models.Model):
    site = models.ForeignKey(SiteModel, on_delete=models.CASCADE, verbose_name='Сайт', default=0, null=True,
                             help_text='Обмен относится только к этому сайту')
    pay_from = models.ForeignKey(PaySystemModel, on_delete=models.CASCADE, verbose_name='Клиент отдаёт',
                                 related_name='pay_from_change', help_text='Получаемая валюта')
    pay_from_min = models.FloatField(verbose_name='Мин', default=0, validators=[validate_more_zero],
                                     help_text=' Значение больше 0')
    pay_from_max = models.FloatField(verbose_name='Макс', default=0, validators=[validate_more_zero],
                                     help_text=' Значение больше 0')
    pay_to = models.ForeignKey(PaySystemModel, on_delete=models.CASCADE, verbose_name='Клиент получает',
                               related_name='pay_to_change', help_text='Отдаваемая валюта')
    pay_to_min = models.FloatField(verbose_name='Мин', default=0, validators=[validate_more_zero],
                                   help_text=' Значение больше 0')
    pay_to_max = models.FloatField(verbose_name='Макс', default=0, validators=[validate_more_zero],
                                   help_text=' Значение больше 0')

    fee = models.FloatField(verbose_name='Комиссия за обмен в %', default=0, help_text='Может быть отрицательной')
    fee_fix = models.FloatField(verbose_name='Фиксированная комиссия', default=0, help_text='В отдаваемой валюте >=0',
                                validators=[validate_zero])
    # todo если есть мин.комиссия то и отдаваемая сумма должна быть не меньше этой комиссии
    fee_min = models.FloatField(verbose_name='Минимальная комиссия', default=0, help_text='В отдаваемой валюте >=0',
                                validators=[validate_zero])
    fee_max = models.FloatField(verbose_name='Максимальная комиссия', default=0, help_text='В отдаваемой валюте >=0',
                                validators=[validate_zero])


    city_change = models.ForeignKey(CityModel, on_delete=models.CASCADE, verbose_name='Город обмена наличных',
                                    null=True, blank=True, help_text='Актуально только для наличных расчётов')


    active = models.BooleanField(default=False, verbose_name='Активно')
    dinamic_fee = models.BooleanField(default=True, verbose_name='Динамическая маржа')
    manual = models.BooleanField(default=False, verbose_name='Ручной обмен', help_text='Наличные расчёты всегда ручные')
    juridical = models.BooleanField(default=False, verbose_name='Перевод со счёта')
    verifying = models.BooleanField(default=False, verbose_name='Документы')
    cardverify = models.BooleanField(default=False, verbose_name='Верификация карты')
    floating = models.BooleanField(default=False, verbose_name='Плавающий курс')
    otherin = models.BooleanField(default=False, verbose_name='Приём на стороннюю пс')
    otherout = models.BooleanField(default=False, verbose_name='Выплата со сторонней пс')
    reg = models.BooleanField(default=False, verbose_name='Регистрация')
    card2card = models.BooleanField(default=False, verbose_name='Перевод на карту')
    confirm_text = models.TextField('Текст на страницу подтверждения для начала обмена',
                                    default='Курс обмена зафиксирован на 15 минут. После 15 минут обмен может быть произведён по курсу, актуальному на момент обработки заявки')
    description_text = models.TextField('Тэг страницы: description', default='Безопасный обмен денег')
    keywords_text = models.TextField('Тэг страницы: keywords', default='qiwi, btc, ltc, usd')
    title_text = models.TextField('Тэг страницы: title', default='Меняй смело!')
    description = models.CharField(max_length=255, blank=True, verbose_name='Комментарий. Для себя')

    def __str__(self):
        return str(self.pay_from) + '->' + str(self.pay_to)

    class Meta:
        verbose_name = 'Обмен'
        verbose_name_plural = 'Направления обмена'
        ordering = ('pay_from', 'pay_to')
