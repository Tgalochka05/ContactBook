from django import forms
import re

class ContactForm(forms.Form):
    name = forms.CharField(
        label='ФИО',
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    phone = forms.CharField(
        label='Телефон',
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    address = forms.CharField(
        label='Адрес',
        max_length=200,
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )

    def clean_name(self):
        name = self.cleaned_data['name']
        if not re.match(r'^[а-яА-Яa-zA-Z\s\-\.]+$', name):
            raise forms.ValidationError('ФИО может содержать только буквы, пробелы, дефисы и точки')
        return name

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        # Простая валидация телефона
        if not re.match(r'^[\+\d\s\-\(\)]+$', phone):
            raise forms.ValidationError('Некорректный формат телефона')
        return phone

class UploadXMLForm(forms.Form):
    xml_file = forms.FileField(
        label='XML файл',
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.xml'})
    )