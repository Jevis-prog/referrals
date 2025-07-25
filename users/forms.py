from django import forms


class PhoneForm(forms.Form):
    phone_number = forms.CharField(label="Номер телефона", max_length=15)


class CodeForm(forms.Form):
    code = forms.CharField(label="Код подтверждения", max_length=4)


class InviteForm(forms.Form):
    invite_code = forms.CharField(label="Инвайт-код", max_length=6)
