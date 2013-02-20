import sys
from apps.cowry.exceptions import PaymentMethodNotFound
from django.utils.importlib import import_module


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


def _adapter_for_payment_method(payment_method_id):
    for adapter in _adapters:
        for pmi in adapter.get_payment_methods():
            if payment_method_id == pmi:
                return adapter
    raise PaymentMethodNotFound(payment_method_id)


def create_payment_object(payment_method_id, payment_submethod='', amount='', currency=''):
    adapter = _adapter_for_payment_method(payment_method_id)
    payment = adapter.create_payment_object(payment_method_id, payment_submethod, amount, currency)
    payment.save()
    return payment


def get_payment_methods(amount=None, currency='', country='', recurring=None, pm_ids=None):
    payment_methods = []
    for adapter in _adapters:
        cur_payment_methods = adapter.get_payment_methods()
        for pm_id in cur_payment_methods:
            if pm_ids is None or pm_id in pm_ids:
                # Extract values from the configuration.
                pm_config = cur_payment_methods[pm_id]
                max_amount = pm_config.get('max_amount', sys.maxint)
                min_amount = pm_config.get('min_amount', 0)
                restricted_currencies = pm_config.get('restricted_currencies', (currency,))
                restricted_countries = pm_config.get('restricted_countries', (country,))
                supports_recurring = pm_config.get('supports_recurring', True)

                # See if we need to exclude the current payment_method (pm).
                add_pm = True
                if amount and (amount > max_amount or amount < min_amount):
                    add_pm = False
                if country not in restricted_countries:
                    add_pm = False
                if currency not in restricted_currencies:
                    add_pm = False
                if recurring and not supports_recurring:
                    add_pm = False

                # For now we only return a few params. Later on we might want to return the entire object.
                if add_pm:
                    payment_methods.append({'id': pm_id, 'name': pm_config.get('name')})

    return payment_methods


def get_payment_method_ids(amount=None, currency='', country='', recurring=None, pm_ids=None):
    payment_method_ids = []
    for pm in get_payment_methods(amount=amount, currency=currency, country=country, recurring=recurring, pm_ids=pm_ids):
        payment_method_ids.append(pm['id'])
    return payment_method_ids


def get_payment_submethods(payment_method_id):
    adapter = _adapter_for_payment_method(payment_method_id)
    for payment_methods in adapter.get_payment_method_config():
        for pmi in payment_methods.keys():
            config = payment_methods[pmi]
            return config.get('submethods')
