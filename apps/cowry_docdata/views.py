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
        if 'order' in request.QUERY_PARAMS:
            order = request.QUERY_PARAMS['order']
            # TODO: Match on this regex when not testing: '^COWRY-([0-9]+)$'. Can only do this when test config setting.
            if re.match('^COWRY-', order):
                # Try to find the payment for this mor.
                try:
                    payment = DocDataPaymentOrder.objects.get(merchant_order_reference=order)
                except DocDataPaymentOrder.DoesNotExist:
                    status_logger.error('Could not find order {0} to update payment status.'.format(order))
                    return response.Response(status=status.HTTP_403_FORBIDDEN)

                # Update the status for the payment.
                status_logger.info('{0}: Processing status changed notification for order {1}.'.format(payment.payment_order_id, order))
                payments.update_payment_status(payment, status_changed_notification=True)

                # Return 200 as required by DocData when the status changed notification was consumed.
                return response.Response(status=status.HTTP_200_OK)
            else:
                status_logger.error('Could not match order {0} to update payment status.'.format(order))
        return response.Response(status=status.HTTP_403_FORBIDDEN)
