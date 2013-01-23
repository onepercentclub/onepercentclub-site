from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from apps.bluebottle_drf2.permissions import AllowNone
from apps.bluebottle_drf2.views import ListCreateAPIView, ListAPIView, RetrieveUpdateDeleteAPIView
from rest_framework import status
from rest_framework import permissions
from rest_framework import response
from rest_framework import generics
from .models import Donation, OrderItem, Order
from .serializers import DonationSerializer, OrderSerializer, OrderItemSerializer


class CartMixin(object):
    def get_or_create_cart(self):
        order_id = self.request.session.get("cart_session")
        # check if we can find the order from sessions
        if order_id:
            try:
                order = Order.objects.get(id=order_id)
            except Order.DoesNotExist:
                # Check if the user has an open order that wasn't in session
                # TODO: Make this work?
                # if self.request.user.is_aunthenticated():
                # order = Order.objects.filter(user=self.request.user).filter(status=Order.OrderStatuses.new).get()
                # if not order:
                order = self.create_cart()
        else:
            order = self.create_cart()
        return order

    def create_cart(self):
        order = Order(created=timezone.now(), status=Order.OrderStatuses.new)
        order.save()
        self.request.session["cart_session"] = order.id
        return order


class OrderList(CartMixin, ListCreateAPIView):
    model = Order
    permission_classes = (AllowNone,)
    serializer_class = OrderSerializer
    paginate_by = 10


class OrderItemList(CartMixin, generics.ListAPIView):
    model = OrderItem
    serializer_class = OrderItemSerializer
    permissions_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        # Filter queryset for the current order
        order = self.get_or_create_cart()
        return order.orderitem_set.all()


class OrderDonationList(CartMixin, generics.ListCreateAPIView):
    model = Donation
    serializer_class = DonationSerializer
    permissions_classes = (permissions.IsAuthenticatedOrReadOnly,)
    paginate_by = 100

    def get_queryset(self):
        # Filter queryset for the current order
        order = self.get_or_create_cart()
        orderitems = order.orderitem_set.filter(content_type=ContentType.objects.get_for_model(Donation))
        queryset = Donation.objects.filter(id__in=orderitems.values('object_id'))
        return queryset

    def create(self, request, *args, **kwargs):
        order = self.get_or_create_cart()
        serializer = self.get_serializer(data=request.DATA)
        if serializer.is_valid():
            self.pre_save(serializer.object)
            self.object = serializer.save()

            self.object.status = Donation.DonationStatuses.new
            if request.user.is_authenticated():
                self.object.user = request.user
            self.object.save()
            orderitem = OrderItem.objects.create(
                item = self.object,
                order = order
            )
            orderitem.save()
            return response.Response(serializer.data, status=status.HTTP_201_CREATED)
        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderDonationDetail(CartMixin, generics.RetrieveUpdateDestroyAPIView):
    model = Donation
    serializer_class = DonationSerializer

    # TODO: Make sure we only return this clients (user or guest) donation
    # TODO: Only UPDATE/DELETE permission if it's in the (active/in progress) cart

    def get_queryset(self):
        # Filter queryset for the current order
        order = self.get_or_create_cart()
        orderitems = order.orderitem_set.filter(content_type=ContentType.objects.get_for_model(Donation))
        queryset = Donation.objects.filter(id__in=orderitems.values('object_id'))
        return queryset



