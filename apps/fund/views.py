from apps.accounts.models import AnonymousProfile
from apps.bluebottle_drf2.serializers import ObjectBasedSerializer
from apps.fund.serializers import OrderProfileSerializer
from cowry.factory import PaymentFactory
from cowry.models import PaymentMethod, Payment, PaymentInfo
from django.contrib.contenttypes.models import ContentType
from apps.bluebottle_drf2.permissions import AllowNone
from apps.bluebottle_drf2.views import ListCreateAPIView, ListAPIView, RetrieveAPIView
from rest_framework import status
from rest_framework import permissions
from rest_framework import response
from rest_framework import generics
from .models import Donation, OrderItem, Order
from .serializers import DonationSerializer, OrderItemSerializer, PaymentMethodSerializer, PaymentSerializer,\
    PaymentInfoSerializer


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
        return order

    def get_or_create_current_order(self):
        order = self.get_current_order()
        if not order:
            order = self.create_current_order()
        return order

    def create_current_order(self):
        user =  self.request.user
        if user.is_authenticated():
            order = Order(user=user, status=Order.OrderStatuses.started)
        else:
            order = Order(status=Order.OrderStatuses.started)
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


class OrderCurrent(RetrieveAPIView):
    # TODO: Implement
    model = Order
    permission_classes = (AllowNone,)


class PaymentList(ListAPIView):
    # TODO: Implement
    model = Payment
    permission_classes = (AllowNone,)
    paginate_by = 10


class PaymentDetail(RetrieveAPIView):
    # TODO: Implement
    model = Payment
    permission_classes = (AllowNone,)


class PaymentInfoList(ListAPIView):
    # TODO: Implement
    model = PaymentInfo
    permission_classes = (AllowNone,)
    paginate_by = 10


class PaymentInfoDetail(RetrieveAPIView):
    # TODO: Implement
    model = PaymentInfo
    permission_classes = (AllowNone,)

# End: Unimplemented API views

class OrderProfile(CurrentOrderMixin, generics.RetrieveUpdateAPIView):

    serializer_class = OrderProfileSerializer

    def get_object(self, queryset=None):
        order = self.get_or_create_current_order()
        if order.user:
            return order.user
        if not order.anonymous_profile:
            order.anonymous_profile = AnonymousProfile.objects.create()
            order.anonymous_profile.save()
            order.save()
        return order.anonymous_profile


class OrderProfileCurrent(CurrentOrderMixin, generics.RetrieveUpdateAPIView):

    serializer_class = OrderProfileSerializer

    def get_object(self, queryset=None):
        order = self.get_or_create_current_order()
        if order.user:
            return order.user
        if not order.anonymous_profile:
            order.anonymous_profile = AnonymousProfile.objects.create()
            order.anonymous_profile.save()
            order.save()
        return order.anonymous_profile


class OrderItemList(CurrentOrderMixin, generics.ListAPIView):
    model = OrderItem
    serializer_class = OrderItemSerializer
    permissions_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        # Filter queryset for the current order
        order = self.get_or_create_current_order()
        return order.orderitem_set.all()


# Note: Not currently being used.
class OrderLatestItemList(OrderItemList):
    """
    This is the return url where the user should be directed to after the payment process is completed
    """
    model = Order
    serializer_class = OrderItemSerializer

    def get_queryset(self):
        order = self.get_current_order()
        if order and order.payment:
            payment_factory = PaymentFactory()
            payment_factory.set_payment(order.payment)
            payment_factory.check_payment()
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
            payment_factory = PaymentFactory()
            payment_factory.set_payment(order.payment)
            payment_factory.check_payment()
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
    paginate_by = 100

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

            donation.status = Donation.DonationStatuses.started
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



# Payment views

class CurrentPaymentMixin(CurrentOrderMixin):
    """
    This mixin provides methods to get/create a Payment connect to the Current Order.
    It also has methods to get/create a PaymentInfo object.
    """

    def get_or_create_current_payment(self):
        # Get or create the Payment for the Current Order
        payment  = self.get_current_payment()
        if payment:
            return payment
        return self.create_current_payment()


    def get_current_payment(self):
        order = self.get_or_create_current_order()
        if order.payment:
            # Always update payment with latest order amount
            order.payment.amount = order.amount
            order.payment.save()
            return order.payment
        return None

    def create_current_payment(self):
        order = self.get_or_create_current_order()
        # TODO: We don't use payment_method now.
        if self.request.DATA and self.request.DATA.get('payment_method', None):
            payment_factory = PaymentFactory()
            payment_factory.set_payment_method(self.request.DATA['payment_method'])
            order.payment = payment_factory.create_payment(amount=order.amount)
            order.save()
            return order.payment

        # If no payment or payment_method then return a Payment object so we can set the payment_method
        payment_factory = PaymentFactory()
        # TODO: For now set hardcoded payment_method=1. Please fix.
        order.payment = payment_factory.create_payment(amount=order.amount)
        order.save()
        return order.payment


    # TODO: Plit this into get, create and get_or_create methods.
    def get_current_payment_info(self):
        payment = self.get_or_create_current_payment()
        payment = self.get_current_payment()
        payment_factory = PaymentFactory()
        payment_factory.set_payment(payment)

        # For now set all customer info from user
        # TODO: Check if info is available
        # TODO: Check which info is required by payment_method
        # TODO: Not always create a payment_info, update if it exists
        user = self.request.user
        if user.is_authenticated():
            if user.get_profile():
                address = user.get_profile().useraddress_set.get()
                payment_info = payment_factory.create_payment_info(amount=payment.amount,
                    first_name=user.first_name, last_name=user.last_name, email=user.email, address=address.line1,
                    zip_code=address.zip_code, city=address.city, country=address.country.alpha2_code)
            else:
                payment_info = payment_factory.create_payment_info(amount=payment.amount,
                    first_name=user.first_name, last_name=user.last_name, email=user.email)
        else:
            payment_info = payment_factory.create_payment_info(amount=payment.amount)
        return payment_info


class PaymentMethodList(generics.ListAPIView):
    model = PaymentMethod
    serializer_class = PaymentMethodSerializer
    paginate_by = 100


class PaymentMethodDetail(generics.RetrieveAPIView):
    model = PaymentMethod
    serializer_class = PaymentMethodSerializer


class PaymentCurrent(CurrentPaymentMixin, generics.RetrieveUpdateDestroyAPIView):
    model = Payment
    serializer_class = PaymentSerializer

    def get_object(self):
        return self.get_or_create_current_payment()


class PaymentInfoCurrent(CurrentPaymentMixin, generics.RetrieveUpdateDestroyAPIView):
    """
    Gather Payment Method specific information about the user.
    """
    # TODO: Gather Payment Method information here. Maybe we can send form information here??
    # TODO: Validation
    model = PaymentInfo
    serializer_class = PaymentInfoSerializer

    def get_object(self):
        return self.get_current_payment_info()

