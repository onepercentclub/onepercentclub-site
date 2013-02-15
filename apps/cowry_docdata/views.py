import re
from apps.cowry import payments
from apps.cowry_docdata.models import DocDataPaymentOrder
from rest_framework import generics
from rest_framework import response
from rest_framework import status

import logging
status_logger = logging.getLogger('cowry-docdata.status')

# TODO: limit status change notifications to docdata IPs
class StatusChangedNotificationView(generics.GenericAPIView):
    def get(self, request, *args, **kwargs):
        if 'mor' in request.QUERY_PARAMS:
            mor = request.QUERY_PARAMS['mor']
            # TODO: Match on this regex when not testing: '^COWRY-([0-9]+)$'. Can only do this when test config setting.
            if re.match('^COWRY-', mor):
                # Try to find the payment for this mor.
                try:
                    payment = DocDataPaymentOrder.objects.get(merchant_order_reference=mor)
                except DocDataPaymentOrder.DoesNotExist:
                    status_logger.error('Cannot find payment for merchant_order_reference: {0}'.format(mor))
                    response.Response(status.HTTP_403_FORBIDDEN)

                # TODO: Can update status as background job.
                # Update the status for the payment.
                status_logger.info('Processing status changed notification for: {0}', mor)
                payments.update_payment_status(payment, status_changed_notification=True)

                # Return 200 as required by DocData when the status changed notification was consumed.
                return response.Response(status.HTTP_200_OK)
            else:
                status_logger.error('merchant_order_reference not correctly matched: {0}'.format(mor))
        return response.Response(status.HTTP_403_FORBIDDEN)
