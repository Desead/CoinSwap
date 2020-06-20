import uuid
from django.db import models
from django.utils.timezone import now
from src.core.models import PaySystemModel, SiteModel, UsedMoneyModel
from django.contrib.auth.models import User


# модель заявки
# todo дата создания - необходимо везде использовтаь одно и тоже время. на фронте в JS используется UTC, здесь
#  необходимо также. или как вариант - вписать сюда дату из JS
# todo uuid заявки надо сделать, именно её показывать в адресной строке, а не номер заявки
class OrderModel(models.Model):
    STATUS_CHOISES = (
        ('ok', 'Выполнена'),
        ('new', 'Новая заявка'),
        ('abort', 'Отменена'),
        ('error', 'Ошибка'),
    )
    LOCK_CHOISES = (
        ('from', 'Отдаваемая сумма'),
        ('to', 'Принимаемая сумма'),
    )
    num = models.PositiveIntegerField(auto_created=True, verbose_name='Номер заявки', default=100, editable=False)
    numuuid = models.CharField(max_length=36, editable=False)
    site = models.ForeignKey(SiteModel, on_delete=models.CASCADE, verbose_name='Сайт', null=True, default=0)
    status = models.CharField(max_length=50, choices=STATUS_CHOISES, default='new', verbose_name='Статус заявки')
    data_create = models.DateTimeField(default=now, verbose_name='Дата создания заявки', editable=False)
    data_change = models.DateTimeField(default=now, verbose_name='Дата изменения заявки')

    pay_from = models.ForeignKey(PaySystemModel, on_delete=models.CASCADE, verbose_name='Клиент отдаёт пс',
                                 related_name='pay_from_order', editable=False)
    pay_to = models.ForeignKey(PaySystemModel, on_delete=models.CASCADE, verbose_name='Клиент получает пс',
                               related_name='pay_to_order', editable=False)
    sum_from = models.FloatField(default=0, verbose_name='Клиент отдаёт')
    sum_to = models.FloatField(default=0, verbose_name='Клиент получает')
    profit = models.FloatField(default=0, verbose_name='Наша прибыль')
    partner = models.FloatField(default=0, verbose_name='Прибыль партнёра')

    # todo так как считаем всё в рублях то валюты рубль в системе должна быть всегда
    sum_from_rub = models.FloatField(default=0, verbose_name='Сколько отдаёт в рублях')
    sum_to_run = models.FloatField(default=0, verbose_name='Клиент получает в рублях')
    profit_rub = models.FloatField(default=0, verbose_name='Наша прибыль в рублях')
    partner_rub = models.FloatField(default=0, verbose_name='Прибыль партнёра в рублях')
    lock = models.CharField(max_length=50, choices=LOCK_CHOISES, default='from', verbose_name='Неизменная')

    rate = models.FloatField(default=0, verbose_name='Курс обмена')
    rate_best = models.FloatField(default=0, verbose_name='Курс на бесте')
    rate_cb = models.FloatField(default=0, verbose_name='Биржевой курс')

    margin = models.FloatField(default=0, verbose_name='Маржа сделки')
    fee_client = models.FloatField(default=0, verbose_name='Пользовательская комиссия')

    # движение денег: wallet_client_from -> wallet_exchange_to; wallet_exchange_from -> wallet_client_to
    wallet_client_from = models.CharField(max_length=16, verbose_name='Кошелёк c которого клиент отдаёт', blank=True,
                                          editable=False)
    wallet_client_to = models.CharField(max_length=50, verbose_name='Кошелёк на который клиент получает',
                                        editable=False)
    wallet_exchange_from = models.CharField(max_length=50, verbose_name='Кошелёк с которого обменник отдаёт',
                                            default='')
    wallet_exchange_to = models.CharField(max_length=50, verbose_name='Кошелёк на который обменник получает',
                                          default='')
    wallet_add = models.CharField(max_length=50, verbose_name='Доп.поле для крипты', blank=True)
    client = models.ForeignKey(User, on_delete=models.CASCADE, editable=False)
    text = models.TextField(verbose_name='Выводимый текст для ручной заявки', blank=True)
    description = models.TextField(blank=True, verbose_name='Комментарий. Для себя')

    def __str__(self):
        return str(self.num) + ': ' + self.pay_from.screen + ' -> ' + self.pay_to.screen

    class Meta:
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки на обмен'
        ordering = ['-num']


# todo нужна проверка чтобы нельзя было создавать дво одинаковых направления обмена
# todo в заявку надо сохранять слепок всех участвующих в обмене цифр, тогда можно будет решить все проблемы
class ChangeModel(models.Model):
    # id_step=models.PositiveSmallIntegerField(default=0, auto_created=True, editable=False)
    site = models.ForeignKey(SiteModel, on_delete=models.CASCADE, verbose_name='Сайт', default=0, null=True)
    pay_from = models.ForeignKey(PaySystemModel, on_delete=models.CASCADE, verbose_name='Клиент отдаёт',
                                 related_name='pay_from_change')
    pay_from_min = models.FloatField(verbose_name='Мин', default=0)
    pay_from_max = models.FloatField(verbose_name='Макс')
    pay_to = models.ForeignKey(PaySystemModel, on_delete=models.CASCADE, verbose_name='Клиент получает',
                               related_name='pay_to_change')
    pay_to_min = models.FloatField(verbose_name='Мин', default=0)
    pay_to_max = models.FloatField(verbose_name='Макс')
    fee = models.FloatField(verbose_name='Комиссия за обмен в %', default=1)
    fee_fix = models.FloatField(verbose_name='Фиксированная комиссия', default=0)
    active = models.BooleanField(default=False, verbose_name='Активно')
    dinamic_fee = models.BooleanField(default=True, verbose_name='Динамическая маржа')
    manual = models.BooleanField(default=False, verbose_name='Ручной обмен')
    juridical = models.BooleanField(default=False, verbose_name='Перевод со счёта')
    verifying = models.BooleanField(default=False, verbose_name='Документы')
    cardverify = models.BooleanField(default=False, verbose_name='Верификация карты')
    floating = models.BooleanField(default=False, verbose_name='Плавающий курс')
    otherin = models.BooleanField(default=False, verbose_name='Приём на стороннюю пс')
    otherout = models.BooleanField(default=False, verbose_name='Выплата со сторонней пс')
    reg = models.BooleanField(default=False, verbose_name='Регистрация')
    card2card = models.BooleanField(default=False, verbose_name='Перевод на карту')
    text = models.TextField(verbose_name='Текст для ручного обмена', blank=True)
    description = models.TextField(blank=True, verbose_name='Комментарий. Для себя')

    def __str__(self):
        return str(self.pay_from) + '->' + str(self.pay_to)

    class Meta:
        verbose_name = 'Обмен'
        verbose_name_plural = 'Направления обмена'
        ordering = ('pay_from', 'pay_to')
