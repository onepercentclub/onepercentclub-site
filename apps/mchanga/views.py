from apps.mchanga.models import MpesaPayment, MpesaFundRaiser
from apps.mchanga.serializers import MpesaPaymentSerializer, MpesaFundRaiserSerializer
from apps.projects.permissions import IsProjectOwner
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
        # if project_slug:
        #     filter_kwargs['project__owner'] = self.request.user
        # else:
        #     return queryset.none()

        return queryset.filter(**filter_kwargs)


class MpesaFundRaiserList(ListAPIView):
    model = MpesaFundRaiser
    serializer_class = MpesaFundRaiserSerializer


class MpesaFundRaiserDetail(RetrieveAPIView):
    model = MpesaFundRaiser
    serializer_class = MpesaFundRaiserSerializer
    lookup_field = 'account'

