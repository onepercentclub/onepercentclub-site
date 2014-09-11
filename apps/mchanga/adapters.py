import urllib2
import simplejson
from apps.mchanga.models import MpesaPayment, MpesaFundRaiser

PAYMENTS_URL = 'https://secure.changa.co.ke/api/tagged/all_payments/format/json'
FUNDRAISER_URL = 'https://secure.changa.co.ke/api/tagged/all_fundrasiers/format/json'


class MchangaService(object):

    def sync_payments(self):
        req = urllib2.Request(PAYMENTS_URL)
        opener = urllib2.build_opener()
        content = opener.open(req)
        payments = simplejson.load(content)
        for payment in payments:
            MpesaPayment.create_from_json(payment)

    def sync_fundraisers(self):
        req = urllib2.Request(FUNDRAISER_URL)
        opener = urllib2.build_opener()
        content = opener.open(req)
        fundraisers = simplejson.load(content)
        for fundraiser in fundraisers:
            MpesaFundRaiser.create_from_json(fundraiser)
