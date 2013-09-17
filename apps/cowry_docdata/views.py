import re
from apps.cowry import payments
from apps.cowry.models import PaymentLogLevels
from rest_framework import generics
from rest_framework import response
from rest_framework import status
from .models import DocDataPaymentOrder, DocDataPaymentLogEntry

import logging
logger = logging.getLogger(__name__)


# TODO: limit status change notifications to docdata IPs
class StatusChangedNotificationView(generics.GenericAPIView):
    def get(self, request, *args, **kwargs):
        if 'order' in request.QUERY_PARAMS:
            order = request.QUERY_PARAMS['order']
            if re.match('^[0-9]+-[0-9]+$', order):
                # Try to find the payment for this order.
                try:
                    payment = DocDataPaymentOrder.objects.get(merchant_order_reference=order)
                except DocDataPaymentOrder.DoesNotExist:
                    logger.error('Could not find order {0} to update payment status.'.format(order))
                    return response.Response(status=status.HTTP_403_FORBIDDEN)

                # Update the status for the payment.
                status_log = DocDataPaymentLogEntry(docdata_payment_order=payment, level=PaymentLogLevels.info)
                status_log.message = 'Received status changed notification for merchant_order_reference {0}.'.format(order)
                status_log.save()
                payments.update_payment_status(payment, status_changed_notification=True)

                # Return 200 as required by DocData when the status changed notification was consumed.
                return response.Response(status=status.HTTP_200_OK)
            else:
                logger.error('Could not match order {0} to update payment status.'.format(order))
        return response.Response(status=status.HTTP_403_FORBIDDEN)
