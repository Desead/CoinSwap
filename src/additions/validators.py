from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_zero(value):
    if value < 0:
        raise ValidationError(
            _('%(value)s Значение должно быть >= 0'),
            params={'value': value},
        )

def validate_more_zero(value):
    if value <= 0:
        raise ValidationError(
            _('%(value)s Значение должно быть больше 0'),
            params={'value': value},
        )
