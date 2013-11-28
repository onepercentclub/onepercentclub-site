import logging
from apps.cowry import factory
from apps.cowry import payments
from apps.cowry.exceptions import PaymentException
from apps.cowry.permissions import IsOrderCreator
from apps.cowry.models import PaymentStatuses, Payment
from apps.cowry.serializers import PaymentSerializer
from apps.cowry_docdata.models import DocDataPaymentOrder
from apps.cowry_docdata.serializers import DocDataOrderProfileSerializer
from apps.fund.serializers import DonationInfoSerializer, NestedDonationSerializer, RecurringOrderSerializer, RecurringDonationSerializer
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.signals import user_logged_in
from django.db import transaction
from django.http import Http404
from rest_framework import exceptions, status, permissions, response, generics
from django.utils.translation import ugettext as _
from .models import Donation, Order, OrderStatuses, DonationStatuses, RecurringDirectDebitPayment
from .permissions import IsUser
from .serializers import DonationSerializer, OrderSerializer, RecurringDirectDebitPaymentSerializer, \
    OrderCurrentSerializer, OrderCurrentDonationSerializer


logger = logging.getLogger(__name__)


#
# Mixins.
#

anon_order_id_session_key = 'cart_order_id'

no_active_order_error_msg = _(u"No active order")


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
        if order and order.id and order.status == OrderStatuses.current and order.recurring == False:
            latest_payment = order.latest_payment
            if latest_payment.payment_order_id and latest_payment.status == PaymentStatuses.in_progress:
                payments.update_payment_status(order.latest_payment)
        return order


class NestedDonationMixin(object):
    model = Donation
    serializer_class = NestedDonationSerializer
    permission_classes = (IsUser,)

    def get_queryset(self):
        qs = super(NestedDonationMixin, self).get_queryset()

        # First filter the default queryset by user.
        qs = qs.filter(user=self.request.user)

        # Second filter the queryset by the order.
        order_id = self.kwargs.get('order_pk')
        return qs.filter(order_id=order_id)

    def pre_save(self, obj):
        # Don't allow donations to be added to closed orders. This check is here and not in the Serializer
        # because we need to access the kwargs to get the order_pk.
        order_id = self.kwargs.get('order_pk')
        order = Order.objects.get(id=order_id)
        if order.status == OrderStatuses.closed:
            raise exceptions.PermissionDenied(_("You cannot add a donation to a closed Order."))

        if self.request.user.is_authenticated():
            obj.user = self.request.user

        obj.order = order


class NestedDonationList(NestedDonationMixin, generics.ListCreateAPIView):
    pass


class NestedDonationDetail(NestedDonationMixin, generics.RetrieveUpdateDestroyAPIView):
    pass


class DonationList(generics.ListAPIView):
    model = Donation
    serializer_class = DonationSerializer
    permission_classes = (IsUser,)

    def get_queryset(self):
        qs = super(DonationList, self).get_queryset()
        return qs.filter(user=self.request.user)


class DonationDetail(generics.RetrieveUpdateDestroyAPIView):
    model = Donation
    serializer_class = DonationSerializer
    permission_classes = (IsUser,)


# Recurring Orders

class RecurringOrderList(generics.ListCreateAPIView):
    model = Order
    serializer_class = RecurringOrderSerializer
    permission_classes = (permissions.IsAuthenticated, IsOrderCreator,)
    filter_fields = ('status',)
    paginate_by = 10

    def get_queryset(self):
        qs = self.model.objects
        qs = qs.filter(recurring=True)
        user = self.request.user
        if isinstance(user, AnonymousUser):
            return qs.none()
        else:
            return qs.filter(user=user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        # Check if there's already an active recurring order
        orders = Order.objects.filter(user=request.user).filter(recurring=True).filter(status=OrderStatuses.recurring)
        if orders.count():
            return response.Response(serializer.errors, status=status.HTTP_403_FORBIDDEN)
        return super(RecurringOrderList, self).create(request, *args, **kwargs)

    def pre_save(self, obj):
        obj.user = self.request.user
        obj.recurring = True
        obj.status = OrderStatuses.recurring


class RecurringOrderDetail(generics.RetrieveUpdateAPIView):
    model = Order
    serializer_class = RecurringOrderSerializer
    permission_classes = (IsOrderCreator,)

    def get_queryset(self):
        qs = self.model.objects
        qs = qs.filter(recurring=True)
        user = self.request.user
        if isinstance(user, AnonymousUser):
            return qs.none()
        else:
            return qs.filter(user=user)

    def get_object(self, queryset=None):
        order = super(RecurringOrderDetail, self).get_object(queryset=queryset)

        # Do a status check with DocData when we don't know the status of in_progress orders.
        if order and order.status == OrderStatuses.recurring and order.recurring == True:
            latest_payment = order.latest_payment
            if latest_payment.payment_order_id and latest_payment.status == PaymentStatuses.in_progress:
                payments.update_payment_status(order.latest_payment)
        return order


class RecurringDonationList(generics.ListCreateAPIView):
    model = Donation
    serializer_class = RecurringDonationSerializer
    permission_classes = (IsUser,)
    paginate_by = 10

    def get_queryset(self):
        qs = super(RecurringDonationList, self).get_queryset()
        qs = qs.filter(donation_type=Donation.DonationTypes.recurring)
        return qs.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        try:
            order = Order.objects.filter(user=request.user, id=request.DATA.get('order')).get()
        except Order.DoesNotExist:
            return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return super(RecurringDonationList, self).create(request, *args, **kwargs)


class RecurringDonationDetail(generics.RetrieveUpdateDestroyAPIView):
    model = Donation
    serializer_class = RecurringDonationSerializer
    permission_classes = (IsUser,)

    def get_queryset(self):
        qs = super(RecurringDonationDetail, self).get_queryset()
        qs = qs.filter(donation_type=Donation.DonationTypes.recurring)
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
            order = Order.objects.get(user=self.request.user, status=OrderStatuses.recurring)
        except Order.DoesNotExist:
            if created:
                obj.delete()
            raise exceptions.ParseError(detail=no_active_order_error_msg)

        # Update monthly order.
        with transaction.commit_on_success():
            monthly_order, created = Order.objects.get_or_create(user=self.request.user, status=OrderStatuses.recurring)
            monthly_order.recurring = True
            monthly_order.save()

        for donation in monthly_order.donations.all():
            donation.order = monthly_order
            donation.save()


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
            # TODO See if we can use something like Django-lazy-user so that the payment profile can always be set with data from the user model.
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
                order = Order.objects.get(user=self.request.user, recurring=False, status=OrderStatuses.current)
                self._update_payment(order)
                return order
            except Order.DoesNotExist:
                return None
        else:
            order_id = self.request.session.get(anon_order_id_session_key)
            if order_id:
                try:
                    order = Order.objects.get(id=order_id, recurring=False, status=OrderStatuses.current)
                    self._update_payment(order)
                    return order
                except Order.DoesNotExist:
                    return None
            else:
                return None

    def get_queryset(self):
        # Filter queryset for the current order
        alias = self.kwargs.get('alias', None)
        order_id = self.kwargs.get('order_pk', None)

        # Deal with the 'current' alias.
        if alias == 'current':
            order = self.get_current_order()
        elif order_id:
            try:
                order = Order.objects.get(user=self.request.user, recurring=False, id=order_id)
            except Order.DoesNotExist:
                raise exceptions.ParseError(detail=_(u"Order not found."))
        else:
            raise exceptions.ParseError(detail=_(u"No order specified."))
        if not order:
            raise exceptions.ParseError(detail=_(u"Order not found."))
        queryset = self.model.objects.filter(order=order)
        return queryset

    def create(self, request, *args, **kwargs):
        order = self.get_current_order()
        if not order:
            raise exceptions.ParseError(detail=no_active_order_error_msg)
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)

        if serializer.is_valid():
            if request.user.is_authenticated():
                setattr(serializer.object, self.user_field, request.user)
            serializer.object.order = order
            self.pre_save(serializer.object)
            self.object = serializer.save(force_insert=True)
            self.post_save(self.object, created=True)

            headers = self.get_success_headers(serializer.data)
            return response.Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
                order, created = Order.objects.get_or_create(user=self.request.user, recurring=False, status=OrderStatuses.current)
        else:
            # An anonymous user could have an order (cart) in the session.
            order_id = self.request.session.get(anon_order_id_session_key)
            if order_id:
                try:
                    order = Order.objects.get(id=order_id, recurring=False, status=OrderStatuses.current)
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


class OrderCurrentDonationList(CurrentOrderMixin, generics.ListCreateAPIView):
    model = Donation
    serializer_class = OrderCurrentDonationSerializer
    paginate_by = 50
    user_field = 'user'


class OrderCurrentDonationDetail(CurrentOrderMixin, generics.RetrieveUpdateDestroyAPIView):
    model = Donation
    serializer_class = OrderCurrentDonationSerializer


def adjust_anonymous_current_order(sender, request, user, **kwargs):
    if anon_order_id_session_key in request.session:
        try:
            anon_current_order = Order.objects.get(id=request.session.pop(anon_order_id_session_key))
            if anon_current_order.status == OrderStatuses.current:

                try:
                    user_current_order = Order.objects.get(user=user, recurring=False, status=OrderStatuses.current)
                    # Close old order by this user.
                    user_current_order.status = OrderStatuses.closed
                    user_current_order.save()

                    # Cancel the payments on the closed order.
                    if user_current_order.payments.count() > 0:
                        for payment in anon_current_order.payments.all():
                            if payment.status != PaymentStatuses.new:
                                try:
                                    payments.cancel_payment(payment)
                                except(NotImplementedError, PaymentException) as e:
                                    logger.warn("Problem cancelling payment on closed user Order {0}: {1}".format(
                                        user_current_order.id, e))

                except Order.DoesNotExist:
                    # There isn't a current order so we don't need to close it.
                    pass

            # Assign the anon order to this user.
            anon_current_order.user = user
            anon_current_order.save()
            # Move all donations to this user too.
            for donation in anon_current_order.donations.all():
                donation.user = user
                donation.save()

        except Order.DoesNotExist:
            pass

user_logged_in.connect(adjust_anonymous_current_order)


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
