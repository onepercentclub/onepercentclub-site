from apps.grouppages.serializers import GroupPageSerializer
from bluebottle.bluebottle_drf2.views import ListCreateAPIView, RetrieveUpdateDeleteAPIView, ListAPIView

from .models import GroupPage
from .permissions import IsOwnerOrReadOnly


class GroupPageList(ListCreateAPIView):
    model = GroupPage
    serializer_class = GroupPageSerializer
    paginate_by = 5


class GroupPageDetail(RetrieveUpdateDeleteAPIView):
    model = GroupPage
    serializer_class = GroupPageSerializer
    permission_classes = (IsOwnerOrReadOnly, )

