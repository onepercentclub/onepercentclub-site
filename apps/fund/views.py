import logging
from apps.cowry import payments
from apps.cowry.permissions import IsOrderCreator
from apps.cowry.models import PaymentStatuses
from apps.cowry_docdata.models import DocDataPaymentOrder, DocDataWebDirectDirectDebit
from apps.cowry_docdata.serializers import DocDataOrderProfileSerializer, DocDataWebDirectDirectDebitSerializer
from django.contrib.contenttypes.models import ContentType
from apps.bluebottle_drf2.permissions import AllowNone
from apps.bluebottle_drf2.views import ListAPIView
from django.db import transaction
from django.http import Http404
from rest_framework import status
from rest_framework import permissions
from rest_framework import response
from rest_framework import generics
from rest_framework import exceptions
from django.utils.translation import ugettext as _
from .mails import mail_voucher_redeemed, mail_custom_voucher_request
from .models import Donation, OrderItem, Order, OrderStatuses, Voucher, CustomVoucherRequest
from .serializers import (DonationSerializer, OrderSerializer, VoucherSerializer, VoucherDonationSerializer,
                          VoucherRedeemSerializer, CustomVoucherRequestSerializer)

logger = logging.getLogger(__name__)


class CurrentOrderMixin(object):
    """ Mixin to get/create a 'current' Order. """

    def _update_payment(self, order):
        def create_new_payment():
            payment = DocDataPaymentOrder()
            payment.save()
            order.payments.add(payment)

        # Create a payment if we need one.
        # We're currently only using DocData so we can directly connect the DocData payment order to the order.
        # Note that Order still has a ManyToMany relationship with 'cowry.Payment'. In the future, we can create
        # the payment at a later stage in the order process using cowry's
        # 'factory.create_new_payment(amount, currency)'.
        latest_payment = order.latest_payment
        if not latest_payment:
            create_new_payment()
            latest_payment = order.latest_payment
        elif latest_payment.status != PaymentStatuses.new:
            if latest_payment.status == PaymentStatuses.in_progress:
                payments.cancel_payment(latest_payment)
                create_new_payment()
                latest_payment = order.latest_payment
            else:
                # TODO Deal with this error somehow.
                logger.error("CurrentOrder retrieved when latest payment has status: {0}".format(latest_payment.status))

        # Update the payment total.
        latest_payment.amount = order.total
        latest_payment.currency = 'EUR'  # The default currency for now.
        latest_payment.save()

    def get_current_order(self):
        if self.request.user.is_authenticated():
            try:
                order = Order.objects.get(user=self.request.user, status=OrderStatuses.current)
                self._update_payment(order)
                return order
            except Order.DoesNotExist:
                return None
        else:
            order_id = self.request.session.get('cart_order_id')
            if order_id:
                try:
                    order = Order.objects.get(id=order_id, status=OrderStatuses.current)
                    self._update_payment(order)
                    return order
                except Order.DoesNotExist:
                    return None
            else:
                return None


# Order views.

no_active_order_error_msg = _(u"No active order")


class OrderList(ListAPIView):
    model = Order
    # TODO Implement and remove AllowNone.
    permission_classes = (AllowNone, IsOrderCreator)
    paginate_by = 10


class OrderDetail(CurrentOrderMixin, generics.RetrieveUpdateAPIView):
    model = Order
    serializer_class = OrderSerializer
    permission_classes = (IsOrderCreator,)

    def _create_anonymous_order(self):
        with transaction.commit_on_success():
            order = Order()
            order.save()
        self.request.session['cart_order_id'] = order.id
        self.request.session.save()
        return order

    def get_or_create_current_order(self):
        if self.request.user.is_authenticated():
            with transaction.commit_on_success():
                order, created = Order.objects.get_or_create(user=self.request.user, status=OrderStatuses.current)
        else:
            # An anonymous user could have an order (cart) in the session.
            order_id = self.request.session.get('cart_order_id')
            if order_id:
                try:
                    order = Order.objects.get(id=order_id, status=OrderStatuses.current)
                except Order.DoesNotExist:
                    # A new order is created if it's not in the db for some reason.
                    order = self._create_anonymous_order()
            else:
                order = self._create_anonymous_order()

        # Create / update the payment object and amount
        self._update_payment(order)

        return order

    def get_object(self, queryset=None):
        alias = self.kwargs.get('alias', None)
        if alias == 'current':
            order = self.get_or_create_current_order()
        else:
            order = super(OrderDetail, self).get_object()
        self.check_object_permissions(self.request, order)

        if not order:
            raise Http404(_(u"No %(verbose_name)s found matching the query") %
                          {'verbose_name': queryset.model._meta.verbose_name})

        # Only try to update the status if we're not using the 'current' alias and the statuses match our expectations.
        if alias != 'current':
            if order.status == OrderStatuses.current and order.latest_payment.payment_order_key and order.latest_payment.status == PaymentStatuses.in_progress:
                payments.update_payment_status(order.latest_payment)

        return order


class PaymentProfileCurrent(CurrentOrderMixin, generics.RetrieveUpdateAPIView):
    """
    Payment profile information.
    """
    model = DocDataPaymentOrder
    serializer_class = DocDataOrderProfileSerializer

    def get_object(self, queryset=None):
        order = self.get_current_order()
        if not order:
            raise exceptions.ParseError(detail=no_active_order_error_msg)
        self.check_object_permissions(self.request, order)
        latest_payment = order.latest_payment

        # We're relying on the fact that the Payment is created when the Order is created. This assert
        # verifies this assumption in case the Order creation code changes in the future.
        assert latest_payment

        # Pre-fill the order profile form if the user is authenticated.
        if self.request.user.is_authenticated():
            latest_payment.customer_id = self.request.user.id
            latest_payment.email = self.request.user.email
            latest_payment.first_name = self.request.user.first_name
            latest_payment.last_name = self.request.user.last_name

            # Try to use the address from the profile if it's set.
            address = self.request.user.address
            if address:
                latest_payment.address = address.line1
                latest_payment.city = address.city
                latest_payment.postal_code = address.postal_code
                if address.country:
                    latest_payment.country = address.country.alpha2_code

            # Try to use the language from the User settings if it's set.
            if self.request.user.primary_language:
                latest_payment.language = self.request.user.primary_language[:2]  # Cut off locale.
        else:
            # Use Netherlands as the default country for anonymous orders.
            # TODO: This should be replaced with a proper ip -> geo solution.
            latest_payment.country = 'NL'

        # Set language from request if required.
        if not latest_payment.language:
            latest_payment.language = self.request.LANGUAGE_CODE[:2]  # Cut off locale.

        latest_payment.save()
        return latest_payment


class DocDataDirectDebitCurrent(CurrentOrderMixin, generics.RetrieveUpdateAPIView):
    """
    DocData direct debit payment for the CurrentOrder.
    """
    model = DocDataWebDirectDirectDebit
    serializer_class = DocDataWebDirectDirectDebitSerializer

    def get_object(self, queryset=None):
        order = self.get_current_order()
        if not order:
            raise exceptions.ParseError(detail=no_active_order_error_msg)
        # Use the order for the permissions of the payment. If a user can access the order, they can access the payment.
        self.check_object_permissions(self.request, order)
        payment = order.latest_payment

        # We're relying on the fact that the Payment is created when the Order is created. This assert
        # verifies this assumption in case the Order creation code changes in the future.
        assert payment

        # This assumes that payment is a DocDataPaymentOrder.
        assert isinstance(payment, DocDataPaymentOrder)
        docdata_payment = payment.latest_docdata_payment
        if not docdata_payment or not isinstance(docdata_payment, DocDataWebDirectDirectDebit):
            docdata_payment = DocDataWebDirectDirectDebit()
            docdata_payment.docdata_payment_order = payment
            docdata_payment.save()

        return docdata_payment


# OrderItems

class OrderItemMixin(object):

    def get_queryset(self):
        # Filter queryset for the current order
        alias = self.kwargs.get('alias', None)
        order_id = self.kwargs.get('order_id', None)
        if alias == 'current':
            order = self.get_current_order()
        elif order_id:
            try:
                order = Order.objects.get(user=self.request.user, id=order_id)
            except Order.DoesNotExist:
                raise exceptions.ParseError(detail=_(u"Order not found."))
        else:
            raise exceptions.ParseError(detail=_(u"No order specified."))
        if not order:
            raise exceptions.ParseError(detail=_(u"Order not found."))
        order_items = order.orderitem_set.filter(content_type=ContentType.objects.get_for_model(self.model))
        queryset = self.model.objects.filter(id__in=order_items.values('object_id'))
        return queryset

    def create(self, request, *args, **kwargs):
        order = self.get_current_order()
        if not order:
            raise exceptions.ParseError(detail=no_active_order_error_msg)
        serializer = self.get_serializer(data=request.DATA)
        if serializer.is_valid():
            self.pre_save(serializer.object)
            obj = serializer.save()

            if request.user.is_authenticated():
                setattr(obj, self.user_field, request.user)
            obj.save()
            orderitem = OrderItem.objects.create(content_object=obj, order=order)
            orderitem.save()
            return response.Response(serializer.data, status=status.HTTP_201_CREATED)
        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        # Tidy up! Delete related OrderItem, if any.
        obj = self.get_object()
        ct = ContentType.objects.get_for_model(obj)
        order_item = OrderItem.objects.filter(object_id=obj.id, content_type=ct)
        if order_item:
            order_item.delete()
        obj.delete()
        return response.Response(status=status.HTTP_204_NO_CONTENT)


class OrderDonationList(OrderItemMixin, CurrentOrderMixin, generics.ListCreateAPIView):
    model = Donation
    serializer_class = DonationSerializer
    paginate_by = 50
    user_field = 'user'


class OrderDonationDetail(OrderItemMixin, CurrentOrderMixin, generics.RetrieveUpdateDestroyAPIView):
    model = Donation
    serializer_class = DonationSerializer


class OrderVoucherList(OrderItemMixin, CurrentOrderMixin, generics.ListCreateAPIView):
    """
    Resource for ordering Vouchers
    """
    model = Voucher
    serializer_class = VoucherSerializer
    permissions_classes = (permissions.IsAuthenticatedOrReadOnly,)
    paginate_by = 50
    user_field = 'sender'


class OrderVoucherDetail(OrderItemMixin, CurrentOrderMixin, generics.RetrieveUpdateDestroyAPIView):
    """
    Resource for changing a Voucher order
    """
    model = Voucher
    serializer_class = VoucherSerializer


class VoucherMixin(object):

    def get_voucher(self):
        """
        Override default to have semantic error responses.
        """
        code = self.kwargs.get('code', None)
        if not code:
            raise exceptions.ParseError(detail=_(u"No gift card code supplied"))
        try:
            voucher = Voucher.objects.get(code=code.upper())
        except Voucher.DoesNotExist:
            raise exceptions.ParseError(detail=_(u"No gift card with that code"))
        if voucher.status != Voucher.VoucherStatuses.paid:
            raise exceptions.PermissionDenied(detail=_(u"Gift card code already used"))
        return voucher


class VoucherDetail(VoucherMixin, generics.RetrieveUpdateAPIView):
    """
    Resource for Voucher redemption
    """
    model = Voucher
    serializer_class = VoucherRedeemSerializer

    def get_object(self, queryset=None):
        voucher = self.get_voucher()
        self.check_object_permissions(self.request, voucher)
        return voucher

    def pre_save(self, obj):
        mail_voucher_redeemed(obj)
        if self.request.user.is_authenticated():
            obj.receiver = self.request.user
        if obj.status == Voucher.VoucherStatuses.cashed:
            for donation in obj.donations.all():
                donation.status = Donation.DonationStatuses.paid
                donation.save()


class VoucherDonationList(VoucherMixin, generics.ListCreateAPIView):
    model = Donation
    serializer_class = VoucherDonationSerializer

    def pre_save(self, obj):
        voucher = self.get_voucher()
        # Clear previous donations for this voucher
        for donation in voucher.donations.all():
            donation.delete()
        obj.amount = voucher.amount

        """
        Keep this code around for if we want to change to multiple donations for one voucher.

        count = len(voucher.donations.all()) + 1
        rest_amount = voucher.amount
        part_amount = floor(voucher.amount / count)
        for donation in voucher.donations.all():
            rest_amount -= part_amount
            donation.amount = part_amount
            donation.save()

        obj.amount = rest_amount
        """

        obj.save()
        voucher.donations.add(obj)

    def get_queryset(self):
        voucher = self.get_voucher()
        return voucher.donations.all()


# Not used yet, until we want multiple donations per voucher
class VoucherDonationDetail(VoucherMixin, generics.RetrieveDestroyAPIView):
    model = Donation
    serializer_class = VoucherDonationSerializer

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        voucher = self.get_voucher()
        count = len(voucher.donations.all()) - 1
        if count:
            part_amount = round(100 * voucher.amount / count) / 100
            rest_amount = voucher.amount
            for donation in voucher.donations.all():
                rest_amount -= part_amount
                donation.amount = part_amount
                donation.save()
            # FIXME There's a bug here - donation is not defined anymore.
            donation.amount += rest_amount
            donation.save()
        obj.delete()
        return response.Response(status=status.HTTP_204_NO_CONTENT)


class CustomVoucherRequestList(generics.ListCreateAPIView):
    model = CustomVoucherRequest
    serializer_class = CustomVoucherRequestSerializer

    def pre_save(self, obj):
        mail_custom_voucher_request(obj)
