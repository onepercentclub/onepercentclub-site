from apps.mchanga.models import MpesaPayment
from apps.mchanga.serializers import MpesaPaymentSerializer
from apps.projects.permissions import IsProjectOwner
from rest_framework.generics import ListAPIView


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
