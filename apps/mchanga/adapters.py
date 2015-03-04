import urllib2
import simplejson
from apps.mchanga.models import MpesaPayment, MpesaFundraiser
from django.conf import settings

PAYMENTS_URL = 'https://secure.changa.co.ke/api/tagged/all_payments/format/json'
FUNDRAISER_URL = 'https://secure.changa.co.ke/api/tagged/all_fundraisers/format/json'
PAYMENT_URL = 'https://secure.changa.co.ke/api/tagged/payment/{0}/format/json'

REALM = 'M-CHANGA API'
USERNAME = settings.MCHANGA_USER
PASSWORD = settings.MCHANGA_PASSWORD


class MchangaService(object):

    def _load_url(self, url):
        # handler = urllib2.Request(url)
        handler = urllib2.HTTPBasicAuthHandler()
        handler.add_password(REALM, url, 'oneperc', 'cheetah')
        opener = urllib2.build_opener(handler)
        urllib2.install_opener(opener)
        content = urllib2.urlopen(url)
        return simplejson.load(content)

    def sync_payments(self):
        data = self._load_url(PAYMENTS_URL)
        for payment in data:
            MpesaPayment.create_from_json(payment)

    def sync_fundraisers(self):
        data = self._load_url(FUNDRAISER_URL)
        for fundraiser in data:
            MpesaFundraiser.create_from_json(fundraiser)

    def sync_payment_by_id(self, payment_id):
        payment_url = PAYMENT_URL.format(payment_id)
        data = self._load_url(payment_url)
        MpesaPayment.create_from_json(data)
