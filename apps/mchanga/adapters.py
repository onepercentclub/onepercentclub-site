import urllib2
import simplejson
from apps.mchanga.models import MpesaPayment

PAYMENTS_URL = 'https://secure.changa.co.ke/api/tagged/all_payments/format/json'


class MchangaService(object):

    def sync_payments(self):
        req = urllib2.Request(PAYMENTS_URL)
        opener = urllib2.build_opener()
        content = opener.open(req)
        payments = simplejson.load(content)
        for payment in payments:
            MpesaPayment.create_from_json(payment)
