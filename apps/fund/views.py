from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from apps.bluebottle_drf2.permissions import AllowNone
from apps.bluebottle_drf2.views import ListCreateAPIView, ListAPIView, RetrieveUpdateDeleteAPIView
from rest_framework import status
from rest_framework import permissions
from rest_framework import response
from .models import Donation, OrderItem, Order
from .serializers import DonationSerializer, OrderSerializer, OrderItemSerializer


class CartMixin(object):
    def get_or_create_cart(self):
        order_id = self.request.session.get("cart_session")
        if order_id:
            try:
                order = Order.objects.get(id=order_id)
            except Order.DoesNotExist:
                order = self.create_cart()
        else:
            order = self.create_cart()
        return order

    def create_cart(self):
        order = Order(created=timezone.now(), status='started')
        order.save()
        self.request.session["cart_session"] = order.id
        return order


class OrderList(CartMixin, ListCreateAPIView):
    model = Order
    permission_classes = (AllowNone,)
    serializer_class = OrderSerializer
    paginate_by = 10


class OrderItemList(ListAPIView):
    model = OrderItem
    serializer_class = OrderItemSerializer
    permissions_classes = (permissions.IsAuthenticatedOrReadOnly,)
    paginate_by = 10


class OrderDonationList(CartMixin, ListCreateAPIView):
    model = Donation
    serializer_class = DonationSerializer
    permissions_classes = (permissions.IsAuthenticatedOrReadOnly,)
    paginate_by = 10

    def get_queryset(self):
        """
        Filter queryset for the current order
        """
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
            orderitem = OrderItem.objects.create(
                item = self.object,
                order = order
            )
            orderitem.save()
            return response.Response(serializer.data, status=status.HTTP_201_CREATED)
        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderDonationDetail(CartMixin, RetrieveUpdateDeleteAPIView):
    model = Donation
    serializer_class = DonationSerializer

    # TODO: Make sure we only return this clients (user or guest) donation
    # TODO: Only UPDATE/DELETE permission if it's in the (active/in progress) cart


