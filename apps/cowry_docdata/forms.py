from django import forms

class PaymentForm(forms.Form):
    firstname = forms.CharField(max_length=100)
    lastname = forms.CharField(max_length=100)
    address = forms.CharField(max_length=100)
    city = forms.CharField(max_length=100)
    country = forms.CharField(max_length=100)
    zip = forms.CharField(max_length=100)
    email = forms.CharField(max_length=100)


class DirectDebitPaymentForm(forms.Form):
    firstname = forms.CharField(max_length=100)
    lastname = forms.CharField(max_length=100)
    address = forms.CharField(max_length=100)
    city = forms.CharField(max_length=100)
    country = forms.CharField(max_length=100)
    zip = forms.CharField(max_length=100)
    email = forms.EmailField(max_length=100)
    bank_account_number = forms.CharField(max_length=100)
