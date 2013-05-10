import threading
from apps.cowry import payments
from apps.cowry.models import Payment
from apps.cowry.serializers import PaymentSerializer
from apps.cowry_docdata.models import DocDataPaymentOrder, DocDataWebDirectDirectDebit
from apps.cowry_docdata.serializers import DocDataOrderProfileSerializer, DocDataWebDirectDirectDebitSerializer
from django.contrib.contenttypes.models import ContentType
from apps.cowry import factory
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


# Lock used in the CurrentOrderMixin. It needs to be outside of Mixin so it's created more than once.
order_lock = threading.Lock()


class CurrentOrderMixin(object):
    """
    Mixin to get/create an 'Current' or 'Latest' Order.
    Current Order has status 'new'. It is linked to a user or stored in session (for anonymous users).
    Latest Order is the latest order by a user.
    """

    def _update_payment(self, order):
            if order.total and order.payments:
                payment = order.payment  # Need to make this variable assignment to modify the payment.
                payment.amount = order.total
                payment.currency = 'EUR'  # The default currency for now.
                payment.save()

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

    def get_or_create_current_order(self):
        created = False
        if self.request.user.is_authenticated():
            # Critical section to avoid duplicate orders.
            with order_lock:
                with transaction.commit_on_success():
                    order, created = Order.objects.get_or_create(user=self.request.user, status=OrderStatuses.current)

                # We're currently only using DocData so we can directly connect the DocData payment order to the order.
                # Note that Order still has a foreign key to 'cowry.Payment'. In the future, we can create the payment
                # at a later stage in the order process using cowry's 'factory.create_new_payment(amount, currency)'.
                if created:
                    payment = DocDataPaymentOrder()
                    payment.save()
                    order.payments.add(payment)
        else:
            # Critical section to avoid duplicate orders.
            # FIXME: This is broken.
            with order_lock:
                # For an anonymous user the order (cart) might be stored in the session
                order_id = self.request.session.get('cart_order_id')
                if order_id:
                    try:
                        order = Order.objects.get(id=order_id, status=OrderStatuses.current)
                    except Order.DoesNotExist:
                        # Set order_id to None so that a new order is created if it's been cleared
                        # from our db for some reason.
                        order_id = None

                if not order_id:
                    with transaction.commit_on_success():
                        order = Order()
                        order.save()
                        created = True
                    # See comment above about creating this DocDataPaymentOrder here.
                    payment = DocDataPaymentOrder()
                    payment.save()
                    order.payments.add(payment)
                    self.request.session['cart_order_id'] = order.id
                    self.request.session.save()

        # Update the payment amount if needed.
        if not created:
            self._update_payment(order)

        return order


# Some API views we still need to implement

class FundApi(CurrentOrderMixin, ListAPIView):
    # TODO: Implement
    """
    Show available API methods
    """
    permission_classes = (AllowNone,)
    paginate_by = 10


class OrderList(ListAPIView):
    # TODO: Implement
    model = Order
    permission_classes = (AllowNone,)
    paginate_by = 10

# End: Unimplemented API views


# Order views.

no_active_order_error_msg = _(u"No active order")


class OrderDetail(CurrentOrderMixin, generics.RetrieveUpdateAPIView):
    model = Order
    serializer_class = OrderSerializer
    # FIXME: make sure right permissions are set.
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

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

        if order.status == OrderStatuses.in_progress:
            payments.update_payment_status(order.payment)

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
        payment = order.payment

        # We're relying on the fact that the Payment is created when the Order is created. This assert
        # verifies this assumption in case the Order creation code changes in the future.
        assert payment

        # Pre-fill the order profile form if the user is authenticated.
        if self.request.user.is_authenticated():
            payment.customer_id = self.request.user.id
            payment.email = self.request.user.email
            payment.first_name = self.request.user.first_name
            payment.last_name = self.request.user.last_name

            # Try to use the address from the profile if it's set.
            profile = self.request.user.get_profile()
            address = profile.address
            if address:
                payment.address = address.line1
                payment.city = address.city
                payment.postal_code = address.postal_code
                payment.country = address.country.alpha2_code

            # Try to use the interface language from the profile if it's set
            if profile.interface_language:
                payment.language = profile.interface_language[:2]  # Cut off locale.
        else:
            # Use Netherlands as the default country for anonymous orders.
            # TODO: This should be replaced with a proper ip -> geo solution.
            payment.country = 'NL'

        # Set language from request if required.
        if not payment.language:
            payment.language = self.request.LANGUAGE_CODE[:2]  # Cut off locale.

        payment.save()
        return order.payment


class PaymentCurrent(CurrentOrderMixin, generics.RetrieveUpdateAPIView):
    """
    View for dealing with the Payment for the CurrentOrder.
    """
    model = Payment
    serializer_class = PaymentSerializer

    def get_object(self, queryset=None):
        order = self.get_current_order()
        if not order:
            raise exceptions.ParseError(detail=no_active_order_error_msg)
        # Use the order for the permissions of the payment. If a user can access the order, they can access the payment.
        self.check_object_permissions(self.request, order)
        payment = order.payment

        # We're relying on the fact that the Payment is created when the Order is created. This assert
        # verifies this assumption in case the Order creation code changes in the future.
        assert payment

        # Clear the payment method if it's not in the list of available methods.
        # Using 'payment.country' like this assumes that payment is a DocDataPaymentOrder.
        assert isinstance(payment, DocDataPaymentOrder)
        available_payment_methods = factory.get_payment_method_ids(amount=payment.amount, currency=payment.currency,
                                                                   country=payment.country, recurring=order.recurring)
        if payment.payment_method_id and not payment.payment_method_id in available_payment_methods:
            payment.payment_method_id = ''
            payment.save()

        return payment


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
        payment = order.payment

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
