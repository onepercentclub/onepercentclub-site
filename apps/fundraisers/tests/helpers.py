from django.utils import timezone
from bluebottle.bluebottle_utils.tests import generate_random_slug

from ..models import FundRaiser


class FundRaiserTestsMixin(object):
    def create_fundraiser(self, owner, project, title=None, amount=5000, deadline=None):
        if not title:
            title = generate_random_slug()
        if deadline is None:
            deadline = timezone.now() + timezone.timedelta(days=28)

        fr = FundRaiser.objects.create(owner=owner, project=project, title=title, amount=amount, deadline=deadline)
        return fr
