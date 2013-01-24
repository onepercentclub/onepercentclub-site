from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from apps.bluebottle_drf2.permissions import AllowNone
from apps.bluebottle_drf2.views import ListCreateAPIView, ListAPIView, RetrieveUpdateDeleteAPIView
from rest_framework import status
from rest_framework import permissions
from rest_framework import response
from rest_framework import generics
from .models import Donation, OrderItem, Order
from .serializers import DonationSerializer, OrderItemSerializer


class CartMixin(object):
    def get_or_create_order(self):
        order_id = self.request.session.get("cart_session")
        # check if we can find the order from sessions
        if order_id:
            try:
                order = Order.objects.get(id=order_id, status=Order.OrderStatuses.cart)
            except Order.DoesNotExist:
                # Check if the user has an open order that wasn't in session
                # TODO: Make this work?
                # if self.request.user.is_aunthenticated():
                # order = Order.objects.filter(user=self.request.user, status=Order.OrderStatuses.cart).get()
                # if not order:
                order = self.create_cart()
        else:
            order = self.create_cart()
        return order

    def create_cart(self):
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



