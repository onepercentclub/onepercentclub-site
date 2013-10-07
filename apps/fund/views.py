import logging
from apps.cowry import factory
from apps.cowry import payments
from apps.cowry.exceptions import PaymentException
from apps.cowry.permissions import IsOrderCreator
from apps.cowry.models import PaymentStatuses, Payment
from apps.cowry.serializers import PaymentSerializer
from apps.cowry_docdata.models import DocDataPaymentOrder
from apps.cowry_docdata.serializers import DocDataOrderProfileSerializer
from apps.fund.serializers import DonationInfoSerializer
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.signals import user_logged_in
from registration.signals import user_registered
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.http import Http404
from rest_framework import mixins, exceptions, status, permissions, response, generics
from django.utils.translation import ugettext as _
from .mails import mail_voucher_redeemed, mail_custom_voucher_request
from .models import Donation, OrderItem, Order, OrderStatuses, Voucher, CustomVoucherRequest, VoucherStatuses, \
    DonationStatuses, RecurringDirectDebitPayment
from .permissions import IsUser
from .serializers import DonationSerializer, OrderSerializer, VoucherSerializer, VoucherDonationSerializer, \
    VoucherRedeemSerializer, CustomVoucherRequestSerializer, RecurringDirectDebitPaymentSerializer, \
    OrderCurrentSerializer, OrderCurrentDonationSerializer


logger = logging.getLogger(__name__)


#
# Mixins.
#

anon_order_id_session_key = 'cart_order_id'

no_active_order_error_msg = _(u"No active order")


class OrderItemDestroyMixin(mixins.DestroyModelMixin):

    def destroy(self, request, *args, **kwargs):
        # Tidy up! Delete related OrderItem, if any.
        obj = self.get_object()
        ct = ContentType.objects.get_for_model(obj)
        order_item = OrderItem.objects.filter(object_id=obj.id, content_type=ct)
        if order_item:
            order_item.delete()
            obj.delete()
            return response.Response(status=status.HTTP_204_NO_CONTENT)
        return response.Response(status=status.HTTP_412_PRECONDITION_FAILED)


class OrderItemMixin(mixins.CreateModelMixin):

    def get_queryset(self):
        # Filter queryset for the current order
        alias = self.kwargs.get('alias', None)
        order_id = self.kwargs.get('order_pk', None)

        # Deal with the 'current' alias.
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
        """ Note; Only used with 'current' Order. """
        order = self.get_current_order()
        if not order:
            raise exceptions.ParseError(detail=no_active_order_error_msg)
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)

        if serializer.is_valid():
            self.pre_save(serializer.object)
            self.object = serializer.save(force_insert=True)
            if request.user.is_authenticated():
                setattr(self.object, self.user_field, request.user)
            self.object.save()
            OrderItem.objects.create(content_object=self.object, order=order)
            self.post_save(self.object, created=True)

            headers = self.get_success_headers(serializer.data)
            return response.Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#
# REST views.
#

class OrderList(generics.ListAPIView):
    model = Order
    serializer_class = OrderSerializer
    permission_classes = (IsOrderCreator,)
    filter_fields = ('status',)
    paginate_by = 10

    def get_queryset(self):
        user = self.request.user
        if isinstance(user, AnonymousUser):
            return self.model.objects.none()
        else:
            return self.model.objects.filter(user=user)


class OrderDetail(generics.RetrieveUpdateAPIView):
    model = Order
    serializer_class = OrderSerializer
    permission_classes = (IsOrderCreator,)

    def get_object(self, queryset=None):
        order = super(OrderDetail, self).get_object(queryset=queryset)
        # Do a status check with DocData when we don't know the status of in_progress orders.
        if order and order.id and order.status == OrderStatuses.current:
            latest_payment = order.latest_payment
            if latest_payment.payment_order_id and latest_payment.status == PaymentStatuses.in_progress:
                payments.update_payment_status(order.latest_payment)
        return order


class NestedDonationList(OrderItemMixin, generics.ListCreateAPIView):
    model = Donation
    serializer_class = DonationSerializer
    permission_classes = (IsUser,)

    def get_queryset(self):
        # First filter the default queryset by user.
        qs = super(NestedDonationList, self).get_queryset().filter(user=self.request.user)

        # Second filter the queryset by the order.
        # TODO put this in OrderItemMixin when 'current' Order goes away.
        order_id = self.kwargs.get('order_pk')
        order = Order.objects.get(id=order_id)
        order_items = order.orderitem_set.filter(content_type=ContentType.objects.get_for_model(self.model))
        return self.model.objects.filter(id__in=order_items.values('object_id'))

    # FIXME: Remove this override when 'current' Order goes away. create shouldn't be overridden, only pre and post save.
    def create(self, request, *args, **kwargs):
        return super(OrderItemMixin, self).create(request, *args, **kwargs)

    def pre_save(self, obj):
        # Don't allow donations to be added to closed orders. This check is here and not in the Serializer
        # because we need to access the kwargs to get the order_pk.
        order_id = self.kwargs.get('order_pk')
        order = Order.objects.get(id=order_id)
        if order.status == OrderStatuses.closed:
            raise exceptions.PermissionDenied(_("You cannot add a donation to a closed Order."))

        if self.request.user.is_authenticated():
            obj.user = self.request.user

    def post_save(self, obj, created=False):
        if created:
            order_id = self.kwargs.get('order_pk')
            orderitem = OrderItem.objects.create(content_object=self.object, order_id=order_id)


class NestedDonationDetail(OrderItemDestroyMixin, generics.RetrieveUpdateDestroyAPIView):
    model = Donation
    serializer_class = DonationSerializer
    permission_classes = (IsUser,)

    def get_queryset(self):
        qs = super(NestedDonationDetail, self).get_queryset()
        return qs.filter(user=self.request.user)


class DonationList(generics.ListAPIView):
    model = Donation
    serializer_class = DonationSerializer
    permission_classes = (IsUser,)

    def get_queryset(self):
        qs = super(DonationList, self).get_queryset()
        return qs.filter(user=self.request.user)


class DonationDetail(OrderItemDestroyMixin, generics.RetrieveUpdateDestroyAPIView):
    model = Donation
    serializer_class = DonationSerializer
    permission_classes = (IsUser,)

    def get_queryset(self):
        qs = super(DonationDetail, self).get_queryset()
        return qs.filter(user=self.request.user)


class RecurringDirectDebitPaymentMixin(object):
    model = RecurringDirectDebitPayment
    serializer_class = RecurringDirectDebitPaymentSerializer
    permission_classes = (IsUser,)

    def get_queryset(self):
        if isinstance(self.request.user, AnonymousUser):
            return self.model.objects.none()
        else:
            return self.model.objects.filter(user=self.request.user)

    def pre_save(self, obj):
        obj.user = self.request.user

    def post_save(self, obj, created=False):
        # TODO: Get the order id from the client for the current order.
        try:
            current_order = Order.objects.get(user=self.request.user, status=OrderStatuses.current)
        except Order.DoesNotExist:
            if created:
                obj.delete()
            raise exceptions.ParseError(detail=no_active_order_error_msg)

        # Update monthly order.
        with transaction.commit_on_success():
            monthly_order, created = Order.objects.get_or_create(user=self.request.user, status=OrderStatuses.recurring)
            monthly_order.recurring = True
            monthly_order.save()

        ct = ContentType.objects.get_for_model(Donation)
        for donation in current_order.donations:
            order_item = OrderItem.objects.get(object_id=donation.id, content_type=ct)
            order_item.order = monthly_order
            order_item.save()


class RecurringDirectDebitPaymentList(RecurringDirectDebitPaymentMixin, generics.ListCreateAPIView):
    pass


class RecurringDirectDebitPaymentDetail(RecurringDirectDebitPaymentMixin, generics.RetrieveUpdateAPIView):
    pass


#
# Non-REST Views (i.e. uses the 'current' order)
#

class CurrentOrderMixin(object):
    """ Mixin to get/create a 'current' Order. """

    def _update_payment(self, order):
        """ Create a payment if we need one and update the order total. """
        def create_new_payment(cancelled_payment=None):
            """ Creates and new payment and copies over the the payment profile from the cancelled payment."""
            # TODO See if we can use something like Django-lazy-user so that the payment profile can always be set with date from the user model.
            payment = DocDataPaymentOrder()
            if cancelled_payment:
                payment.email = cancelled_payment.email
                payment.first_name = cancelled_payment.first_name
                payment.last_name = cancelled_payment.last_name
                payment.address = cancelled_payment.address
                payment.postal_code = cancelled_payment.postal_code
                payment.city = cancelled_payment.city
                payment.country = cancelled_payment.country

            payment.order = order
            payment.save()

        # Create a payment if we need one.
        # We're currently only using DocData so we can directly connect the DocData payment order to the order.
        # In the future, we can create the payment at a later stage in the order process using cowry's
        # 'factory.create_new_payment(amount, currency)'.
        latest_payment = order.latest_payment
        if not latest_payment:
            create_new_payment()
            latest_payment = order.latest_payment
        elif latest_payment.status != PaymentStatuses.new:
            if latest_payment.status == PaymentStatuses.in_progress:
                # FIXME: This is not a great way to handle payment cancel failures because they user won't be notified.
                # FIXME: Move to RESTful API for payment cancel / order.
                try:
                    payments.cancel_payment(latest_payment)
                except(NotImplementedError, PaymentException) as e:
                    order.status = OrderStatuses.closed
                    order.save()
                else:
                    create_new_payment(latest_payment)
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
            order_id = self.request.session.get(anon_order_id_session_key)
            if order_id:
                try:
                    order = Order.objects.get(id=order_id, status=OrderStatuses.current)
                    self._update_payment(order)
                    return order
                except Order.DoesNotExist:
                    return None
            else:
                return None


class OrderCurrentDetail(CurrentOrderMixin, generics.RetrieveUpdateAPIView):
    model = Order
    serializer_class = OrderCurrentSerializer
    permission_classes = (IsOrderCreator,)

    def _create_anonymous_order(self):
        with transaction.commit_on_success():
            order = Order()
            order.save()
        self.request.session[anon_order_id_session_key] = order.id
        self.request.session.save()
        return order

    def get_or_create_current_order(self):
        if self.request.user.is_authenticated():
            with transaction.commit_on_success():
                order, created = Order.objects.get_or_create(user=self.request.user, status=OrderStatuses.current)
        else:
            # An anonymous user could have an order (cart) in the session.
            order_id = self.request.session.get(anon_order_id_session_key)
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
            order = super(OrderCurrentDetail, self).get_object()
        self.check_object_permissions(self.request, order)

        if not order:
            raise Http404(_(u"No %(verbose_name)s found matching the query") %
                          {'verbose_name': queryset.model._meta.verbose_name})

        # Don't allow anonymous users to set recurring orders. This check is here and not in the Serializer
        # because we need to access the request to see if a user is authenticated or not.
        if not self.request.user.is_authenticated() and 'recurring' in self.request.DATA and self.request.DATA['recurring']:
            raise exceptions.PermissionDenied(_("Anonymous users are not permitted to create recurring orders."))

        # Only try to update the status if we're not using the 'current' alias and the statuses match our expectations.
        if alias != 'current':
            if order.status == OrderStatuses.current and order.latest_payment.payment_order_id and order.latest_payment.status == PaymentStatuses.in_progress:
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
        payment = order.latest_payment

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


class OrderCurrentDonationList(OrderItemMixin, CurrentOrderMixin, generics.ListCreateAPIView):
    model = Donation
    serializer_class = OrderCurrentDonationSerializer
    paginate_by = 50
    user_field = 'user'


class OrderCurrentDonationDetail(OrderItemMixin, OrderItemDestroyMixin, CurrentOrderMixin, generics.RetrieveUpdateDestroyAPIView):
    model = Donation
    serializer_class = OrderCurrentDonationSerializer


def adjust_anonymous_current_order(sender, request, user, **kwargs):
    if anon_order_id_session_key in request.session:
        try:
            anon_current_order = Order.objects.get(id=request.session.pop(anon_order_id_session_key))
            if anon_current_order.status == OrderStatuses.current:

                # Anonymous order has status 'current' - copy over to user's 'current' order.
                try:
                    user_current_order = Order.objects.get(user=user, status=OrderStatuses.current)
                    # Close old order by this user.
                    user_current_order.status = OrderStatuses.closed
                    user_current_order.save()
                except Order.DoesNotExist:
                    # There isn't a current order for the so we don't need to cancel it.
                    pass
                # Assign the anon order to this user.
                anon_current_order.user = user
                anon_current_order.save()
                # Move all donations to this user too.
                for donation in anon_current_order.donations:
                    donation.user = user
                    donation.save()

            else:
                # Anonymous cart order does not have status 'current' - just assign it to the user.
                anon_current_order.user = user
                anon_current_order.save()
                for donation in anon_current_order.donations:
                    donation.user = user
                    donation.save()
        except Order.DoesNotExist:
            pass

user_logged_in.connect(adjust_anonymous_current_order)


def link_anonymous_donations(sender, user, request, **kwargs):
    """
    Search for anonymous donations with the same email address as this user and connect them.
    """
    print "Connect to " + user.email
    dd_orders = DocDataPaymentOrder.objects.filter(email=user.email).all()
    print "Found orders " + str(len(dd_orders))
    for dd_order in dd_orders:
        dd_order.customer_id = user.id
        dd_order.save()
        dd_order.order.user = user
        dd_order.order.save()
        for donation in dd_order.order.donations:
            donation.user = user
            donation.save()
            # TODO: Also link donation Wall Post to this user

# On account activation try to connect anonymous donations to this user.
user_registered.connect(link_anonymous_donations)


class OrderVoucherList(OrderItemMixin, CurrentOrderMixin, generics.ListCreateAPIView):
    """
    Resource for ordering Vouchers
    """
    model = Voucher
    serializer_class = VoucherSerializer
    permissions_classes = (permissions.IsAuthenticatedOrReadOnly,)
    paginate_by = 50
    user_field = 'sender'


class OrderVoucherDetail(OrderItemMixin, OrderItemDestroyMixin, CurrentOrderMixin,generics.RetrieveUpdateDestroyAPIView):
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
        if voucher.status != VoucherStatuses.paid:
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
        if obj.status == VoucherStatuses.cashed:
            for donation in obj.donations.all():
                donation.status = DonationStatuses.paid
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


# For showing the latest donations
class TickerList(generics.ListAPIView):
    model = Donation
    serializer_class = DonationInfoSerializer
    permission_classes = (permissions.IsAdminUser,)
    paginate_by = 20

    def get_queryset(self):
        qs = super(TickerList, self).get_queryset()
        qs = qs.order_by('-created')
        return qs.filter(status__in=[DonationStatuses.pending, DonationStatuses.paid])
