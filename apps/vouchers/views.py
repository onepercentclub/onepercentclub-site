import logging
from apps.fund.models import DonationStatuses, Donation
from apps.fund.views import CurrentOrderMixin
from rest_framework import exceptions, status, permissions, response, generics
from django.utils.translation import ugettext as _
from .mails import mail_voucher_redeemed, mail_custom_voucher_request
from .models import Voucher, CustomVoucherRequest, VoucherStatuses
from .serializers import VoucherSerializer, VoucherDonationSerializer, VoucherRedeemSerializer, \
    CustomVoucherRequestSerializer


logger = logging.getLogger(__name__)


class OrderVoucherList(CurrentOrderMixin, generics.ListCreateAPIView):
    """
    Resource for ordering Vouchers
    """
    model = Voucher
    serializer_class = VoucherSerializer
    permissions_classes = (permissions.IsAuthenticatedOrReadOnly,)
    paginate_by = 50
    user_field = 'sender'


class OrderVoucherDetail(CurrentOrderMixin, generics.RetrieveUpdateDestroyAPIView):
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