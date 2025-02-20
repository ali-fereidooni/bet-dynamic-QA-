from django import forms
from .models import Question, Form


class FormModelForm(forms.ModelForm):
    class Meta:
        model = Form
        fields = ('name', 'question')
