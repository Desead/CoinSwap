from django import forms
from src.parsers.models import CBRF


class CBRFForm(forms.ModelForm):
    city = forms.CharField(label='Город', widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'idnewmy'}))

    class Meta(object):
        model = CBRF
        fields = ('name', 'nominal_1', 'nominal_2', 'base', 'profit', 'source',)
