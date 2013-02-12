from apps.cowry.models import Payment
from django.db import models
from django.utils.translation import ugettext as _
from djchoices.choices import DjangoChoices, ChoiceItem


# DocData Payment Order Statuses
# ==============================
#
# started - As soon as an order reached the DocData payment menu, the status of the transaction will be started.
#
# paid - As soon as DocData has received the confirmation from a financial institution that the money is withdrawn from
#        the consumers bank account or credit card or when DocData has received the amount on their bank statement, the
#        status will be 'paid'.
#
# closed_canceled - When a consumer enters the payment menu and then decides not to pay, he can leave the payment menu
#                   by using the 'cancel' button. The transaction then will get the status 'closed_canceled'.
#
# closed_expired - When a payment isn't finished properly by the consumer, which means didn't select a payment method
#                  to finish the payment or did not pay eventually, the transaction will expire and the status will
#                  change to closed_expired. The merchant can communicate to the docdata system when a transaction
#                  should expire.
#
# closed_insufficientpaid - When a consumer will pay via a bank transfer it is possible that they will transfer an
#                           amount less then the registered amount. Then the status of the transaction remains started
#                           and the customer will be advised to pay the rest of the amount. As soon as the expire period
#                           is reached, the status of the transaction will change to 'closed_insufficientpaid'.
#
# closed_succes - The payment that DocData has received from the consumer is taken into a payout report and has been
#                 paid to the merchant.


class DocDataPayment(Payment):
    class PaymentStatuses(DjangoChoices):
        started = ChoiceItem('started', label=_("started"))
        paid = ChoiceItem('paid', label=_("Paid"))
        closed_canceled = ChoiceItem('closed_canceled', label=_("Closed Canceled"))
        closed_expired = ChoiceItem('closed_expired', label=_("Closed Expired"))
        closed_insufficientpaid = ChoiceItem('closed_insufficientpaid', label=_("Closed Insufficient Paid"))
        closed_succes = ChoiceItem('closed_succes', label=_("Closed Succes"))

    order_status = models.CharField(_("status"), max_length=25, choices=PaymentStatuses.choices, default=PaymentStatuses.started)

    payment_order_key = models.CharField(max_length=255, default='', blank=True)
    merchant_order_reference = models.CharField(max_length=100, default='', blank=True)

    # Order profile information.
    customer_id = models.IntegerField(default=0)  # Defaults to 0 for anonymous.
    email = models.EmailField(max_length=254, default='')
    first_name = models.CharField(max_length=200, default='')
    last_name = models.CharField(max_length=200, default='')
    street = models.CharField(max_length=200, default='')
    house_number = models.CharField(max_length=20, default='')
    postal_code = models.CharField(max_length=20, default='')
    city = models.CharField(max_length=200, default='')
    country = models.CharField(max_length=2, default='')
    language = models.CharField(max_length=2, default='en')


# DocData Payment Method Statuses
# ===============================
#
# new - As soon as the consumer has reached the payment menu he chooses a payment method. As soon as the payment method
#       is chosen and no further action has been taken, the status of the payment method will be 'new'. So when a
#       payment method has this status, the payment will not arrive unless it's a bank transfer and the consumer did go
#       to their bank and made the transfer without finishing the process according to steps mentioned on the computer
#       screen. All other payment methods will not be collected.
#
# started - As soon as the consumer chooses a payment method and follows the instructions on the screen, the status of
#           the payment method will change to 'started'. In most cases this means DocData has made a connection to the
#           financial institution to withdraw the money from the bank account, credit card or wallet. In case of the
#           direct debit, this means that the consumer filled in his correct bank details and we can sent this
#           information to the bank to withdraw the money.
#
# paid - DocData has received the payment approval from the financial institution for this specific transaction. This
#        status can be reached immediately with the so called direct payment methods like credit card, Paypal or iDEAL.
#        When a consumer chooses this payment method, DocData immediately seeks contact with the financial institution
#        and the outcome will be immediately presented. Payment methods such as a bank transfer will reach the status
#        paid as soon as DocData has received the amount on their bank statement. This could be within a couple of days
#        after placing the order, but it could also take longer. It depends on the time frame within the consumer
#        transfers the money.
#
# canceled - When a payment method has the status canceled, it means that the consumer choose not to proceed with this
#            payment (method) or that the payment was declined by the financial institution. The consumer then can
#            choose to pay with another payment method or choose to cancel the order completely.
#
# refund - The status refund means that DocData has refunded the amount to the customer's credit card, bank account or
#          wallet. A refund will only be executed when docdata payments receives a request from the merchant to refund
#          this amount to the customer. It is possible to only refund not the complete, but just a part of the paid
#          amount.
#
# chargeback - The status chargeback will be shown when a payment has been charged back from the credit card acquirer or
#              bank because of a direct debit that could not be collected or was collected by mistake.


class PaymentMethodStatuses(DjangoChoices):
    new = ChoiceItem('new', label=_("New"))
    started = ChoiceItem('started', label=_("Started"))
    paid = ChoiceItem('paid', label=_("Paid"))
    canceled = ChoiceItem('canceled', label=_("Canceled"))
    refund = ChoiceItem('refund', label=_("Refund"))
    chargeback = ChoiceItem('chargeback', label=_("Chargeback"))


class DocDataWebMenuPaymentMethod(models.Model):
    docdata_payment_method_status = models.CharField(_("status"), max_length=15, choices=PaymentMethodStatuses.choices, default=PaymentMethodStatuses.new)

    docdatapaymentorder = models.ForeignKey(DocDataPayment)
    payment_url = models.URLField(max_length=500, blank=True)


# TODO: Implement this. It's here just to give an idea of future architecture.
# class DocDataWebDirectDirectDebitPaymentMethod(models.Model):
#     docdatapaymentorder = models.ForeignKey(DocDataPayment)
#     bank_account = models.CharField(max_length=20, default='', blank=True)