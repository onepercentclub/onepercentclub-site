import logging
from serializers import LatestDonationSerializer
from bluebottle.donations.models import Donation
from bluebottle.utils.utils import StatusDefinition
from rest_framework import permissions, generics

from bluebottle.utils.model_dispatcher import get_project_model

PROJECT_MODEL = get_project_model()

logger = logging.getLogger(__name__)

# For showing the latest donations
class LatestDonationsList(generics.ListAPIView):
    model = Donation
    serializer_class = LatestDonationSerializer
    permission_classes = (permissions.IsAdminUser,)
    paginate_by = 20

    def get_queryset(self):
        qs = super(LatestDonationsList, self).get_queryset()
        qs = qs.order_by('-created')
        return qs.filter(order__status__in=[StatusDefinition.PENDING, StatusDefinition.SUCCESS])
