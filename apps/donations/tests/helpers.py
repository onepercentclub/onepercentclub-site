import uuid

from apps.fund.models import Donation, Order


class DonationTestsMixin(object):
    def create_order(self, user, **kwargs):
        # Default values.
        creation_kwargs = {
            'user': user,
            'order_number': unicode(uuid.uuid4())[0:30],  # Unique enough...
        }

        creation_kwargs.update(kwargs)

        return Order.objects.create(**creation_kwargs)

    def create_donation(self, user, project, **kwargs):
        # Default values.
        creation_kwargs = {
            'amount': 100,
            'user': user,
            'project': project,
        }

        creation_kwargs.update(kwargs)

        if 'order' not in creation_kwargs:
            creation_kwargs['order'] = self.create_order(user)

        return Donation.objects.create(**creation_kwargs)