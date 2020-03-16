from django import forms
from .models import *


class EEGForm(forms.ModelForm):
    class Meta:
        model = EEG
        fields = ('address', 'name')


class CallForm(forms.ModelForm):
    class Meta:
        model = Call
        fields = ('caller', 'callee')


class CalleeForm(forms.ModelForm):
    class Meta:
        model = Callee
        fields = ('token', 'name')
