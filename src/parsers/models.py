from django.db import models

from src.core.models import UsedMoneyModel


# базовая модель для парсера
class RatesBase(models.Model):
    autocheck = models.BooleanField(default=True, verbose_name='Автоматическое обновление (пока не активно)')
    name = models.CharField(max_length=30, verbose_name='Название')
    base = models.CharField(max_length=30, verbose_name='Базовая валюта')
    profit = models.CharField(max_length=30, verbose_name='Валюта деньги')
    nominal_1 = models.FloatField(verbose_name='Номинал базы')
    nominal_2 = models.FloatField(verbose_name='Курс обмена')
    dt = models.DateTimeField(verbose_name='Время получения', auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        abstract = True


# курсы обмена с цбрф
class CBRF(RatesBase):
    source = models.CharField(max_length=20, verbose_name='Источник получения', default='ЦБРФ')

    class Meta:
        verbose_name = 'ЦБРФ: валюта'
        verbose_name_plural = 'Курсы обменов: ЦБРФ'
        ordering = ('-source', 'name')


# курсы обмена с бинанса
class Binance(RatesBase):
    source = models.CharField(max_length=20, verbose_name='Источник получения', default='Binance')

    class Meta:
        verbose_name = 'Binance: валюта'
        verbose_name_plural = 'Курсы обменов: Binance'
        ordering = ('source', 'name')


# сливаем все курсы в одну талицу+ рассчитываем се возможные кроссы.
class AllRates(RatesBase):
    source = models.CharField(max_length=20, verbose_name='Источник получения')

    def __str__(self):
        return self.base+' -> '+self.profit

    class Meta:
        verbose_name = 'валюта'
        verbose_name_plural = 'Курсы обменов: все'
        ordering = ['name']


class BSexchange(models.Model):
    idexch = models.IntegerField(verbose_name='ID обменника')
    name = models.CharField(max_length=40, verbose_name='Название обменника')
    ignore = models.BooleanField(default=False, verbose_name='Игнорировать обменник')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Bestchange: обменник'
        verbose_name_plural = 'Bestchange: обменники'
        ordering = ['name']

# class BSrates(models.Model):
#     curfrom = models.IntegerField()
#     curto = models.IntegerField()
#     exch = models.IntegerField(default=1)
#     ratefrom = models.FloatField()
#     rateto = models.FloatField()
#     res = models.FloatField()
#     dt = models.DateTimeField(verbose_name='Время получения')
#
#     class Meta:
#         verbose_name = 'Bestchange: курс обмена'
#         verbose_name_plural = 'Bestchange: курсы обменов'
#         ordering = ('curfrom', 'curto')
#
#     name = models.CharField(max_length=30, verbose_name='Название')
#     nominal_1 = models.FloatField(verbose_name='Номинал базы')
#     nominal_2 = models.FloatField(verbose_name='Курс обмена')
#     base = models.CharField(max_length=30, verbose_name='Базовая валюта')
#     profit = models.CharField(max_length=30, verbose_name='Валюта деньги')
#     dt = models.DateTimeField(verbose_name='Время получения', auto_now=True)
#     source = models.CharField(max_length=20, verbose_name='Источник получения')
