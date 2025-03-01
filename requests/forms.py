from .models import ImageModel
from django import forms
from .models import Form, Users


class FormModelForm(forms.ModelForm):
    class Meta:
        model = Form
        fields = ['name', 'slug']

        def __init__(self, *args, **kwargs):
            form_instance = kwargs.pop('form_instance', None)
            super().__init__(*args, **kwargs)

            if form_instance:
                if form_instance.username:
                    self.fields['username'] = forms.CharField(
                        max_length=20, required=True, label="نام کاربری"
                    )
                if form_instance.phone_number:
                    self.fields['phone_number'] = forms.CharField(
                        max_length=11, required=True, label="شماره تلفن"
                    )


class DynamicUserForm(forms.ModelForm):
    class Meta:
        model = Form
        fields = []  # فیلدهای اصلی فرم

    def __init__(self, *args, **kwargs):
        form_instance = kwargs.pop('form_instance', None)
        super().__init__(*args, **kwargs)

        if form_instance:
            if form_instance.username:
                self.fields['username'] = forms.CharField(
                    max_length=20, required=True, label="Username"
                )
            if form_instance.phone_number:
                self.fields['phone_number'] = forms.CharField(
                    max_length=11, required=True, label="Phone number"
                )


class MyModelForm(forms.ModelForm):
    class Meta:
        model = ImageModel
        fields = ['title', 'image']
