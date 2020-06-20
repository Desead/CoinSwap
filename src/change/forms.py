from .models import OrderModel
from django import forms


# class OrderModelForm(forms.ModelForm):
#     class Meta:
#         model = OrderModel
#         fields = ('pay_from', 'sum_from', 'pay_to', 'sum_to')

class HTMLform(forms.Form):
    nm1 = forms.CharField(label='Money2Money')
    nm2 = forms.BooleanField()
    nm3 = forms.FileField()
    nm4 = forms.DateTimeField()
