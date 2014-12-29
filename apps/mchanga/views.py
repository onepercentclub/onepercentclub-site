from apps.mchanga.models import MpesaPayment, MpesaFundraiser
from apps.mchanga.serializers import MpesaPaymentSerializer, MpesaFundraiserSerializer
from bluebottle.projects.permissions import IsProjectOwner
from django.http.response import HttpResponse
from django.views.generic.base import View
from rest_framework.generics import ListAPIView, RetrieveAPIView


class MpesaPaymentList(ListAPIView):
    model = MpesaPayment
    permission_classes = (IsProjectOwner, )
    serializer_class = MpesaPaymentSerializer

    def get_queryset(self):

        # The super handles basic filtering.
        queryset = super(MpesaPaymentList, self).get_queryset()

        project_slug = self.request.QUERY_PARAMS.get('project', None)

        filter_kwargs = {}

        # Only return a list if the requested user is the fundraiser or campaigner.
        if project_slug:
            filter_kwargs['project__owner'] = self.request.user
        else:
            return queryset.none()

        return queryset.filter(**filter_kwargs)


class MpesaFundraiserList(ListAPIView):
    model = MpesaFundraiser
    serializer_class = MpesaFundraiserSerializer


class MpesaFundraiserDetail(RetrieveAPIView):
    model = MpesaFundraiser
    serializer_class = MpesaFundraiserSerializer
    lookup_field = 'account'

"""
Core view
"""


class PaymentStatusChangedView(View):
    """
    This is listening to M-Changa IPN calls.
    """

    def _sync_payment(self, payment_id):
        from .adapters import MchangaService
        service = MchangaService()
        # For now just sync everything
        # service.sync_payment_by_id(payment_id)
        service.sync_payments()
        service.sync_fundraisers()

    def get(self, request, **kwargs):

        payment_id = None
        if hasattr(kwargs, 'payment_id'):
            payment_id = kwargs['payment_id']
        elif 'mmp_trx_code' in request.GET:
            payment_id = request.GET['mmp_trx_code']
        self._sync_payment(payment_id)
        return HttpResponse('success')

    def post(self, request, **kwargs):
        payment_id = None

        if hasattr(kwargs, 'payment_id'):
            payment_id = kwargs['payment_id']
        elif 'mmp_trx_code' in request.GET:
            payment_id = request.GET['mmp_trx_code']
        self._sync_payment(payment_id)
        return HttpResponse('success')
