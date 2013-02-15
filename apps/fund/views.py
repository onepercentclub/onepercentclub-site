from apps.cowry_docdata.models import DocDataPaymentOrder, DocDataWebDirectDirectDebit, DocDataWebMenu
from apps.cowry_docdata.serializers import DocDataOrderProfileSerializer, DocDataPaymentMethodSerializer
from apps.fund.serializers import PaymentMethodSerializer
from django.contrib.contenttypes.models import ContentType
from apps.cowry import payments, factory
from apps.bluebottle_drf2.permissions import AllowNone
from apps.bluebottle_drf2.views import ListAPIView, RetrieveAPIView
from rest_framework import status
from rest_framework import permissions
from rest_framework import response
from rest_framework import generics
from rest_framework import views
from .models import Donation, OrderItem, Order
from .serializers import (DonationSerializer, OrderItemSerializer, OrderSerializer)
from .utils import get_order_payment_methods

# API views

class CurrentOrderMixin(object):
    """
    Mixin to get/create an 'Current' or 'Latest' Order.
    Current Order has status 'started'. It is linked to a user or stored in session (for anonymous users).
    Latest Order is the latest order by a user.
    """

    def get_current_order(self):
        if self.request.user.is_authenticated():
            try:
                order = Order.objects.get(user=self.request.user, status=Order.OrderStatuses.started)
            except Order.DoesNotExist:
                return None
        else:
            # For an anonymous user the order (cart) might be stored in the session
            order_id = self.request.session.get("cart_session")
            if order_id:
                try:
                    order = Order.objects.get(id=order_id, status=Order.OrderStatuses.started)
                except Order.DoesNotExist:
                    # The order_id was not a cart in the db, return None
                    return None
            else:
                # No order_id in session. Return None
                return None
        order.payment.amount = int(100 * order.amount)
        order.payment.currency = 'EUR'
        order.payment.save()
        return order

    def get_or_create_current_order(self):
        order = self.get_current_order()
        if not order:
            order = self.create_current_order()
        if not self.has_permission(self.request, order):
            self.permission_denied(self.request)
        return order

    def create_current_order(self):
        user = self.request.user
        if user.is_authenticated():
            order = Order(user=user)
        else:
            order = Order()
        # We're currently only using DocData so we can directly connect the DocData payment order to the order. Note
        # that Order still has a foreign key to 'cowry.Payment'. In the future, we can create the payment at a later
        # stage in the order process using cowry's 'factory.create_new_payment(amount, currency)'.
        payment = DocDataPaymentOrder()
        payment.save()
        order.payment = payment
        order.save()
        self.request.session["cart_session"] = order.id
        return order

    def get_latest_order(self):
        if self.request.user.is_authenticated():
            try:
                order = Order.objects.filter(user=self.request.user).exclude(status=Order.OrderStatuses.started).order_by("-created").all()[0]
            except Order.DoesNotExist:
                return None
        else:
            # For an anonymous user the order (cart) might be stored in the session
            order_id = self.request.session.get("cart_session")
            if order_id:
                try:
                    order = Order.objects.get(id=order_id)
                except Order.DoesNotExist:
                    # The order_id was not a Order in the db, return None
                    return None
            else:
                # No order_id in session. Return None
                return None
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


class OrderDetail(RetrieveAPIView):
    # TODO: Implement
    model = Order
    permission_classes = (AllowNone,)

# End: Unimplemented API views


class OrderCurrent(CurrentOrderMixin, generics.RetrieveUpdateAPIView):
    model = Order
    serializer_class = OrderSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_object(self, queryset=None):
        # For now generate payment url over here.
        order = self.get_or_create_current_order()
        # This will save it in pm info.
        if order.payment.payment_method_id:
            payments.get_payment_url(order.payment)
        return order

    def put(self, request, *args, **kwargs):
        # for now we write payment method here because serializer isn't smart enough.
        pm = request.DATA.get('payment_method_id', None)
        if pm:
            order = self.get_or_create_current_order()
            order.payment.payment_method_id = pm
            order.payment.save()

        psm = request.DATA.get('payment_submethod_id', None)
        if psm:
            order = self.get_or_create_current_order()
            order.payment.payment_submethod_id = psm
            order.payment.save()


        return self.update(request, *args, **kwargs)


class OrderItemList(CurrentOrderMixin, generics.ListAPIView):
    model = OrderItem
    serializer_class = OrderItemSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        # Filter queryset for the current order
        order = self.get_or_create_current_order()
        return order.orderitem_set.all()


# Note: Not currently being used (but the OrderLatestDontationList is being used).
class OrderLatestItemList(OrderItemList):
    """
    This is the return url where the user should be directed to after the payment process is completed
    """
    model = Order
    serializer_class = OrderItemSerializer

    def get_queryset(self):
        order = self.get_current_order()
        if order and order.payment:
            payments.update_payment_status(order.payment)
            # TODO: Have a proper check if donation went ok. Signals!
            order.status = Order.OrderStatuses.pending
            order.save()
        else:
            order = self.get_latest_order()

        order.status = Order.OrderStatuses.pending
        order.save()
        return order.orderitem_set.all()


class OrderLatestDonationList(CurrentOrderMixin, generics.ListAPIView):
    model = Donation
    serializer_class = DonationSerializer
    paginate_by = 100

    def get_queryset(self):
        order = self.get_current_order()
        if order and order.payment:
            payments.update_payment_status(order.payment)
            # TODO: Check the status we get back from PSP and set order status accordingly.
            order.status = Order.OrderStatuses.pending
            order.save()
        else:
            order = self.get_latest_order()
        orderitems = order.orderitem_set.filter(content_type=ContentType.objects.get_for_model(Donation))
        queryset = Donation.objects.filter(id__in=orderitems.values('object_id'))
        return queryset


class OrderDonationList(CurrentOrderMixin, generics.ListCreateAPIView):
    model = Donation
    serializer_class = DonationSerializer
    paginate_by = 50

    def get_queryset(self):
        # Filter queryset for the current order
        order = self.get_or_create_current_order()
        orderitems = order.orderitem_set.filter(content_type=ContentType.objects.get_for_model(Donation))
        queryset = Donation.objects.filter(id__in=orderitems.values('object_id'))
        return queryset

    def create(self, request, *args, **kwargs):
        order = self.get_or_create_current_order()
        serializer = self.get_serializer(data=request.DATA)
        if serializer.is_valid():
            self.pre_save(serializer.object)
            donation = serializer.save()

            if request.user.is_authenticated():
                donation.user = request.user
            donation.save()
            orderitem = OrderItem.objects.create(content_object=donation, order=order)
            orderitem.save()
            return response.Response(serializer.data, status=status.HTTP_201_CREATED)
        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderDonationDetail(CurrentOrderMixin, generics.RetrieveUpdateDestroyAPIView):
    model = Donation
    serializer_class = DonationSerializer

    def get_queryset(self):
        # Filter queryset for the current order
        order = self.get_or_create_current_order()
        orderitems = order.orderitem_set.filter(content_type=ContentType.objects.get_for_model(Donation))
        queryset = Donation.objects.filter(id__in=orderitems.values('object_id'))
        return queryset

    def destroy(self, request, *args, **kwargs):
        # Tidy up! Delete related OrderItem, if any.
        obj = self.get_object()
        ct = ContentType.objects.get_for_model(obj)
        order_item = OrderItem.objects.filter(object_id=obj.id, content_type=ct)
        if order_item:
            order_item.delete()
        obj.delete()
        return response.Response(status=status.HTTP_204_NO_CONTENT)


class PaymentOrderProfileCurrent(CurrentOrderMixin, generics.RetrieveUpdateAPIView):
    """
    Payment profile information.
    """
    serializer_class = DocDataOrderProfileSerializer

    def get_object(self):
        order = self.get_or_create_current_order()
        payment = order.payment
        if payment and self.request.user.is_authenticated():
            payment.customer_id = self.request.user.id
            payment.email = self.request.user.email
            payment.first_name = self.request.user.first_name
            payment.last_name = self.request.user.last_name

            profile = self.request.user.get_profile()
            address = profile.address

            payment.language = profile.interface_language
            payment.street = address.line1
            payment.city = address.city
            payment.postal_code = address.zip_code
            payment.country = address.country.alpha2_code
            payment.save()
        else:
            payment.language = self.request.LANGUAGE_CODE
        return order.payment


class PaymentMethodList(CurrentOrderMixin, generics.GenericAPIView):
    """
    Payment Methods
    """

    serializer_class = PaymentMethodSerializer

    def get(self, request, format=None):
        """
        Get the Payment methods form Cowry.
        """
        order = self.get_or_create_current_order()
        ids = request.QUERY_PARAMS.getlist('ids[]', [])
        pms = factory.get_payment_methods(amount=order.amount, currency='EUR', country='NL', recurring=order.recurring, ids=ids)
        serializer = self.get_serializer(pms)
        return response.Response(serializer.data)


# Not implemented nor being used right now.
class PaymentMethodDetail(generics.GenericAPIView):
    """
    Payment Method
    """
    serializer_class = PaymentMethodSerializer


class PaymentMethodInfoCurrent(CurrentOrderMixin, generics.RetrieveUpdateAPIView):
    """
    Payment method information.
    """
    serializer_class = DocDataPaymentMethodSerializer

    def get_object(self):
        order = self.get_or_create_current_order()
        if not order.payment.latest_docdata_payment:
            if not order.payment.payment_method_id:
                payment_methods = get_order_payment_methods(order)
                if payment_methods:
                    order.payment.payment_method_id = payment_methods[0]
                    order.save()
                else:
                    return None
            # TODO: Use cowry factory for this?
            # TODO: Hardcoded stuff is fun! should fix this though.
            if order.recurring:
                payment_method_object = DocDataWebDirectDirectDebit(docdata_payment_order=order.payment)
            else:
                payment_method_object = DocDataWebMenu(docdata_payment_order=order.payment)
            payment_method_object.save()
        return order.payment.latest_docdata_payment



