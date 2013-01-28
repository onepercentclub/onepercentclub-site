from apps.bluebottle_drf2.serializers import PolymorphicSerializer
from apps.fund.serializers import PaymentMethodSerializer, PaymentSerializer, PaymentProcessSerializer
from cowry.factory import PaymentFactory
from cowry.models import PaymentMethod, Payment
from cowry_docdata.models import DocdataPaymentProcess
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from apps.bluebottle_drf2.permissions import AllowNone
from apps.bluebottle_drf2.views import ListCreateAPIView, ListAPIView, RetrieveUpdateDeleteAPIView
from rest_framework import status
from rest_framework import permissions
from rest_framework import response
from rest_framework import generics
from django.views.generic import View
from .models import Donation, OrderItem, Order
from .serializers import DonationSerializer, OrderItemSerializer



class CartMixin(object):

    def get_or_create_order(self):
        # see if the user already has a order (with status 'cart') in the database
        if self.request.user.is_authenticated():
            try:
                order = Order.objects.get(user=self.request.user, status=Order.OrderStatuses.cart)
            except Order.DoesNotExist:
                # If we can't find a order (cart) for this user create one
                order = self.create_order()
        else:
            # For an anonymous user the order (cart) might be stored in the session
            order_id = self.request.session.get("cart_session")
            if order_id:
                try:
                    order = Order.objects.get(id=order_id, status=Order.OrderStatuses.cart)
                except Order.DoesNotExist:
                    # The order_id was not a cart in the db, create a new order (cart)
                    order = self.create_order()
            else:
                # No order_id in session. Create a new order (cart)
                order = self.create_order()

        return order

    def create_order(self):
        order = Order(created=timezone.now(), status=Order.OrderStatuses.cart)
        if self.request.user.is_authenticated():
            order.user = self.request.user
        order.save()
        self.request.session["cart_session"] = order.id
        return order


# API views

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
        if order.payment:
            order.payment.amount = order.amount
            return order.payment
        payment_factory = PaymentFactory()
        payment = payment_factory.create_payment(amount=order.amount)
        if self.request.user.is_authenticated():
            payment.user = self.request.user
        payment.save()
        order.payment = payment
        order.status = Order.OrderStatuses.cart
        order.save()
        return payment


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



class CustomerInfoDetail(CurrentPaymentMixin, generics.RetrieveUpdateAPIView):
    model = DocdataPaymentProcess
    serializer_class = PaymentProcessSerializer

    def get_object(self):
        payment = self.get_payment()
        payment_factory = PaymentFactory()
        payment_factory.set_payment(payment)
        user = self.request.user
        address = user.get_profile().useraddress_set.get()
        return payment_factory.get_payment_process(
            first_name=user.first_name, last_name=user.last_name, email=user.email, address=address.line1,
            zip_code=address.zip_code, city=address.city, country='NL')


class PaymentStatusDetail(CurrentPaymentMixin, generics.RetrieveUpdateAPIView):
    model = DocdataPaymentProcess
    serializer_class = PaymentProcessSerializer

    def get_object(self):
        payment = self.get_payment()
        payment_factory = PaymentFactory()
        payment_factory.set_payment(payment)
        payment_factory.check_payment()
        return payment_factory.get_payment_process()
