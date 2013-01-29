from apps.fund.serializers import PaymentMethodSerializer, PaymentSerializer, DocdataPaymentInfoSerializer, PaymentInfoSerializer
from cowry.factory import PaymentFactory
from cowry.models import PaymentMethod, Payment, PaymentInfo
from django.utils.translation import ugettext as _
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from apps.bluebottle_drf2.permissions import AllowNone
from apps.bluebottle_drf2.views import ListCreateAPIView, ListAPIView, RetrieveUpdateDeleteAPIView
from django.http import Http404
from rest_framework import status
from rest_framework import permissions
from rest_framework import response
from rest_framework import generics
from .models import Donation, OrderItem, Order
from .serializers import DonationSerializer, OrderItemSerializer


# API views

class CartMixin(object):

    def get_order(self):
        if self.request.user.is_authenticated():
            try:
                order = Order.objects.get(user=self.request.user, status=Order.OrderStatuses.cart)
            except Order.DoesNotExist:
                return None
        else:
            # For an anonymous user the order (cart) might be stored in the session
            order_id = self.request.session.get("cart_session")
            if order_id:
                try:
                    order = Order.objects.get(id=order_id, status=Order.OrderStatuses.cart)
                except Order.DoesNotExist:
                    # The order_id was not a cart in the db, return None
                    return None
            else:
                # No order_id in session. Return None
                return None
        return order

    def get_or_create_order(self):
        order = self.get_order()
        if not order:
            order = self.create_order()
        return order

    def create_order(self):
        order = Order(created=timezone.now(), status=Order.OrderStatuses.cart)
        if self.request.user.is_authenticated():
            order.user = self.request.user
        order.save()
        self.request.session["cart_session"] = order.id
        return order


class OrderList(CartMixin, ListCreateAPIView):
    model = Order
    permission_classes = (AllowNone,)
    paginate_by = 10


class OrderItemList(CartMixin, generics.ListAPIView):
    model = OrderItem
    serializer_class = OrderItemSerializer
    permissions_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        # Filter queryset for the current order
        order = self.get_or_create_order()
        return order.orderitem_set.all()


class OrderDonationList(CartMixin, generics.ListCreateAPIView):
    model = Donation
    serializer_class = DonationSerializer
    paginate_by = 100

    def get_queryset(self):
        # Filter queryset for the current order
        order = self.get_or_create_order()
        orderitems = order.orderitem_set.filter(content_type=ContentType.objects.get_for_model(Donation))
        queryset = Donation.objects.filter(id__in=orderitems.values('object_id'))
        return queryset

    def create(self, request, *args, **kwargs):
        order = self.get_or_create_order()
        serializer = self.get_serializer(data=request.DATA)
        if serializer.is_valid():
            self.pre_save(serializer.object)
            donation = serializer.save()

            donation.status = Donation.DonationStatuses.cart
            if request.user.is_authenticated():
                donation.user = request.user
            donation.save()
            orderitem = OrderItem.objects.create(content_object=donation, order=order)
            orderitem.save()
            return response.Response(serializer.data, status=status.HTTP_201_CREATED)
        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderDonationDetail(CartMixin, generics.RetrieveUpdateDestroyAPIView):
    model = Donation
    serializer_class = DonationSerializer

    def get_queryset(self):
        # Filter queryset for the current order
        order = self.get_or_create_order()
        orderitems = order.orderitem_set.filter(content_type=ContentType.objects.get_for_model(Donation))
        queryset = Donation.objects.filter(id__in=orderitems.values('object_id'))
        return queryset



# Payment views

class CurrentPaymentMixin(CartMixin):

    def get_payment(self):
        order = self.get_or_create_order()
        payment_factory = PaymentFactory()

        if order.payment:
            return order.payment

        if self.request.DATA and self.request.DATA['payment_method']:
            payment_factory.set_payment_method(self.request.DATA['payment_method'])
            order.payment = payment_factory.create_payment(amount=order.amount)
            order.save()
            return order.payment

        # If no payment or payment_method then return a plain Payment object so we can set the payment_method
        return Payment.objects.create(amount=order.amount)

    def get_payment_info(self):
        order = self.get_or_create_order()
        payment_factory = PaymentFactory()
        payment_factory.set_payment(order.payment)

        # For now set all customer info from user
        # TODO: Check if info is available
        # TODO: Check which info is required by payment_method
        # TODO: Not always create a payment_info, update if it exists
        user = self.request.user
        address = user.get_profile().useraddress_set.get()
        order.payment.payment_info = payment_factory.create_payment_info(amount=order.amount,
            first_name=user.first_name, last_name=user.last_name, email=user.email, address=address.line1,
            zip_code=address.zip_code, city=address.city, country='nl')

        return order.payment.payment_info


class PaymentMethodList(generics.ListAPIView):
    model = PaymentMethod
    serializer_class = PaymentMethodSerializer
    paginate_by = 100


class PaymentMethodDetail(generics.RetrieveAPIView):
    model = PaymentMethod
    serializer_class = PaymentMethodSerializer


class CheckoutDetail(CurrentPaymentMixin, generics.RetrieveUpdateDestroyAPIView):
    model = Payment
    serializer_class = PaymentSerializer

    def get_object(self):
        return self.get_payment()


class PaymentInfoDetail(CurrentPaymentMixin, generics.RetrieveUpdateDestroyAPIView):
    model = PaymentInfo
    serializer_class = PaymentInfoSerializer

    def get_object(self):
        return self.get_payment_info()


class PaymentStatusDetail(CurrentPaymentMixin, generics.RetrieveUpdateAPIView):
    model = Payment
    serializer_class = PaymentSerializer

    def get_object(self):
        # TODO: maybe also try to get an Order with changed status so API returns an Payment with updated status...
        order = self.get_order()
        if not order:
            raise Http404(_(u"No Order with status 'cart' found in session."))
        order.status = self.kwargs['status']
        order.save()
        payment = order.payment
        if not payment:
            raise Http404(_(u"No Payment found in session."))
        payment_factory = PaymentFactory()
        payment_factory.set_payment(payment)
        payment_factory.check_payment()
        return payment_factory.get_payment()
