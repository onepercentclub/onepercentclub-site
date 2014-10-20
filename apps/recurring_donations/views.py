from apps.recurring_donations.models import MonthlyDonor, MonthlyDonorProject
from apps.recurring_donations.permissions import IsOwner, IsDonor
from apps.recurring_donations.serializers import MonthlyDonationSerializer, MonthlyDonationProjectSerializer
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated


class MonthlyDonationList(generics.ListCreateAPIView):
    model = MonthlyDonor
    permission_classes = (IsAuthenticated, )
    serializer_class = MonthlyDonationSerializer

    def get_queryset(self):
        qs = super(MonthlyDonationList, self).get_queryset()
        return qs.filter(user=self.request.user)

    def pre_save(self, obj):
        self.user = self.request.user


class MonthlyDonationDetail(generics.RetrieveUpdateAPIView):
    model = MonthlyDonor
    permission_classes = (IsOwner, )
    serializer_class = MonthlyDonationSerializer


class MonthlyDonationProjectList(generics.CreateAPIView):
    model = MonthlyDonorProject
    permission_classes = (IsDonor, )
    serializer_class = MonthlyDonationProjectSerializer


class MonthlyDonationProjectDetail(generics.RetrieveUpdateDestroyAPIView):
    model = MonthlyDonorProject
    permission_classes = (IsDonor, )
    serializer_class = MonthlyDonationProjectSerializer

