from bluebottle.bluebottle_utils.tests import generate_random_slug

from ..models import FundRaiser


class FundRaiserTestsMixin(object):
    def create_fundraiser(self, owner, project, title=None, amount=5000):
        if not title:
            title = generate_random_slug()

        fr = FundRaiser.objects.create(owner=owner, project=project, title=title, amount=amount)
        return fr
