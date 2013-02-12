from apps.cowry.exceptions import PaymentMethodNotFound
from django.utils.importlib import import_module
from .models import Payment


def _load_from_module(path):
    package, attr = path.rsplit('.', 1)
    module = import_module(package)
    return getattr(module, attr)

# TODO read django settings to find out what adapters to load.
# TODO Ensure not duplicate payment method names.
# ADAPTERS = getattr(settings, 'COWRY_ADAPTERS')
ADAPTERS = ('apps.cowry_docdata.adapters.DocdataPaymentAdapter',)

_adapters = []
for adapter_str in ADAPTERS:
    adapter_class = _load_from_module(adapter_str)
    _adapters.append(adapter_class())


def _adapter_for_payment_method(payment_method):
    for adapter in _adapters:
        for method in adapter.get_payment_methods():
            if payment_method == method:
                return adapter
    raise PaymentMethodNotFound(payment_method)

def create_payment_object(payment_method, amount='', currency='', payment_submethod=''):
    adapter = _adapter_for_payment_method(payment_method)
    payment = adapter.create_payment_object(payment_method,  amount, currency, payment_submethod)
    payment.save()
    return payment

def get_payment_methods(country=None, amount=None, currency=None):
   # TODO: Filter this based on country, amount and currency.
   payment_methods = []
   for adapter in _adapters:
       for method in adapter.get_payment_methods():
           payment_methods.append(method)
   return payment_methods


def get_payment_submethods(payment_method):
   # TODO: Move this and above to init.
   for adapter in _adapters:
       for method in adapter.get_payment_methods():
           if payment_method == method:
               return adapter.get_payment_submethods(payment_method)
               # TODO payment_method doesn't exist.
   return ''
